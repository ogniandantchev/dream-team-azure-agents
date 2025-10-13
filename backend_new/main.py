# File: main.py
from fastapi import FastAPI, Depends, UploadFile, HTTPException, Query, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2AuthorizationCodeBearer
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import schemas, crud
from database import CosmosDB
import os
import uuid
from contextlib import asynccontextmanager
from fastapi.responses import StreamingResponse, Response
import json, asyncio
from agent_framework_helper import AgentFrameworkHelper, generate_session_name
import logging
from datetime import datetime 
from schemas import AutoGenMessage
from typing import List
import time

print("Starting the Agent Framework server...")

session_data = {}
AGENT_FRAMEWORK_DEFAULT_AGENTS = [
    {
        "input_key":"0001",
        "type":"MagenticOne",
        "name":"Coder",
        "system_message":"",
        "description":"",
        "icon":"👨‍💻"
    },
    {
        "input_key":"0002",
        "type":"MagenticOne",
        "name":"WebSurfer",
        "system_message":"",
        "description":"",
        "icon":"🏄‍♂️"
    },
    {
        "input_key":"0003",
        "type":"MagenticOne",
        "name":"FileSurfer",
        "system_message":"",
        "description":"",
        "icon":"📂"
    },
]

# Lifespan handler for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code: initialize database and configure logging
    app.state.db = CosmosDB()
    logging.basicConfig(level=logging.WARNING,
                        format='%(levelname)s: %(asctime)s - %(message)s')
    print("Database initialized.")
    yield
    # Shutdown code
    app.state.db = None

app = FastAPI(lifespan=lifespan)

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure AD Authentication (Mocked for example)
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    tokenUrl="https://login.microsoftonline.com/common/oauth2/v2.0/token"
)

async def validate_token(token: str = None):
    # In production, implement proper token validation
    print("Token:", token)
    return {"sub": "user123", "name": "Test User"}  # Mocked user data

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_agent_icon(agent_name) -> str:
    if agent_name == "MagenticOneOrchestrator":
        agent_icon = "🎻"
    elif agent_name == "WebSurferAgent":
        agent_icon = "🏄‍♂️"
    elif agent_name == "CoderAgent":
        agent_icon = "👨‍💻"
    elif agent_name == "FileSurferAgent":
        agent_icon = "📂"
    elif agent_name == "user":
        agent_icon = "👤"
    else:
        agent_icon = "🤖"
    return agent_icon

async def display_log_message(streaming_event, logs_dir, session_id, user_id, conversation=None):
    """Convert Agent Framework StreamingEvent to AutoGenMessage format"""
    _user_id = user_id
    
    _response = AutoGenMessage(
        time=streaming_event.time,
        session_id=session_id,
        session_user=_user_id
    )

    _response.type = streaming_event.event_type
    _response.source = streaming_event.source
    _response.content = streaming_event.content
    _response.stop_reason = streaming_event.stop_reason
    _response.content_image = streaming_event.content_image

    # Save to database
    _ = crud.save_message(
        id=None,  # auto-generated
        user_id=_user_id,
        session_id=session_id,
        message=_response.to_json(),
        agents=None,
        run_mode_locally=None,
        timestamp=_response.time
    )

    return _response

# Azure Services Setup (Mocked for example)
blob_service_client = BlobServiceClient.from_connection_string(
    "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;" + \
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;" + \
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)

# Chat Endpoint
@app.post("/chat")
async def chat_endpoint(
    message: schemas.ChatMessageCreate,
    user: dict = Depends(validate_token)
):
    mock_response = "This is a mock AI response using Agent Framework (Markdown formatted)."
    # Log the user message.
    crud.save_message(
        user_id=user["sub"],
        session_id="session_direct",
        message={"content": message.content, "role": "user"}
    )
    # Log the AI response message.
    response = {
        "time": get_current_time(),
        "type": "DirectResponse",
        "source": "AgentFramework",
        "content": mock_response,
        "stop_reason": None,
        "models_usage": None,
        "content_image": None,
    }
    crud.save_message(
        user_id=user["sub"],
        session_id="session_direct",
        message=response
    )

    return Response(content=json.dumps(response), media_type="application/json")

# Start Agent Framework session
@app.post("/start", response_model=schemas.ChatMessageResponse)
async def start_agent_session(
    message: schemas.ChatMessageCreate,
    user: dict = Depends(validate_token)
):
    logger = logging.getLogger("start_agent_session")
    logger.setLevel(logging.INFO)
    logger.info(f"Starting Agent Framework session with message: {message.content}")
    
    _user_id = message.user_id if message.user_id else user["sub"]
    logger.info(f"User ID: {_user_id}")
    _agents = json.loads(message.agents) if message.agents else AGENT_FRAMEWORK_DEFAULT_AGENTS
    _session_id = generate_session_name()
    
    conversation = crud.save_message(
        id=uuid.uuid4(),
        user_id=_user_id,
        session_id=_session_id,
        message={"content": message.content, "role": "user"},
        agents=_agents,
        run_mode_locally=False,
        timestamp=get_current_time()
    )

    logger.info(f"Conversation saved with session_id: {_session_id} and user_id: {_user_id}")
    
    # Return session_id as the conversation identifier
    db_message = schemas.ChatMessageResponse(
        id=uuid.uuid4(),
        content=message.content,
        response=_session_id,
        timestamp="2021-01-01T00:00:00",
        user_id=_user_id,
        orm_mode=True
    )
    return db_message

# Streaming Chat Endpoint using Agent Framework
@app.get("/chat-stream")
async def agent_chat_stream(
    session_id: str = Query(...),
    user_id: str = Query(...),
    user: dict = Depends(validate_token)
):
    logger = logging.getLogger("agent_chat_stream")
    logger.setLevel(logging.WARNING)
    logger.info(f"Agent Framework chat stream started for session_id: {session_id} and user_id: {user_id}")
    
    # Create folder for logs if not exists
    logs_dir = "./logs"
    if not os.path.exists(logs_dir):    
        os.makedirs(logs_dir)

    # Get the conversation from the database using user and session id
    conversation = crud.get_conversation(user_id, session_id)
    logger.info(f"Conversation retrieved: {conversation}")
    
    # Get first message from the conversation
    first_message = conversation["messages"][0]
    # Get the task from the first message as content
    task = first_message["content"]
    print("Task:", task)

    _run_locally = conversation["run_mode_locally"]
    _agents = conversation["agents"]

    # Initialize the Agent Framework system with user_id
    agent_helper = AgentFrameworkHelper(
        logs_dir=logs_dir, 
        save_screenshots=False, 
        run_locally=_run_locally, 
        user_id=user_id
    )
    logger.info(f"Initializing Agent Framework with agents: {len(_agents)} and session_id: {session_id} and user_id: {user_id}")
    await agent_helper.initialize(agents=_agents, session_id=session_id)
    logger.info(f"Initialized Agent Framework with agents: {len(_agents)} and session_id: {session_id} and user_id: {user_id}")

    stream, cancellation_token = agent_helper.main(task=task)
    logger.info(f"Stream and cancellation token created for task: {task}")

    async def event_generator(stream, conversation):
        async for streaming_event in stream:
            json_response = await display_log_message(
                streaming_event=streaming_event, 
                logs_dir=logs_dir, 
                session_id=agent_helper.session_id, 
                conversation=conversation, 
                user_id=user_id
            )    
            yield f"data: {json.dumps(json_response.to_json())}\n\n"

    return StreamingResponse(event_generator(stream, conversation), media_type="text/event-stream")

@app.get("/stop")
async def stop(session_id: str = Query(...)):
    try:
        print("Stopping session:", session_id)
        cancellation_token = session_data[session_id].get("cancellation_token")
        if cancellation_token:
            cancellation_token.cancel()
            return {"status": "success", "message": f"Session {session_id} cancelled successfully."}
        else:
            return {"status": "error", "message": "Cancellation token not found."}
    except Exception as e:
        print(f"Error stopping session {session_id}: {str(e)}")
        return {"status": "error", "message": f"Error stopping session: {str(e)}"}

# Conversations endpoints (unchanged)
@app.post("/conversations")
async def list_all_conversations(
    request_data: dict,
    user: dict = Depends(validate_token)
):
    try:
        user_id = request_data.get("user_id")
        page = request_data.get("page", 1)
        page_size = request_data.get("page_size", 20)
        conversations = app.state.db.fetch_user_conversatons(
            user_id=None, 
            page=page, 
            page_size=page_size
        )
        return conversations
    except Exception as e:
        print(f"Error retrieving conversations: {str(e)}")
        return {"conversations": [], "total_count": 0, "page": 1, "total_pages": 1}

@app.post("/conversations/user")
async def list_user_conversation(request_data: dict = None, user: dict = Depends(validate_token)):
    session_id = request_data.get("session_id") if request_data else None
    user_id = request_data.get("user_id") if request_data else None
    conversations = app.state.db.fetch_user_conversation(user_id, session_id=session_id)
    return conversations

@app.post("/conversations/delete")
async def delete_conversation(session_id: str = Query(...), user_id: str = Query(...), user: dict = Depends(validate_token)):
    logger = logging.getLogger("delete_conversation")
    logger.setLevel(logging.INFO)
    logger.info(f"Deleting conversation with session_id: {session_id} for user_id: {user_id}")
    try:
        result = app.state.db.delete_user_conversation(user_id=user_id, session_id=session_id)
        if result:
            logger.info(f"Conversation {session_id} deleted successfully.")
            return {"status": "success", "message": f"Conversation {session_id} deleted successfully."}
        else:
            logger.warning(f"Conversation {session_id} not found.")
            return {"status": "error", "message": f"Conversation {session_id} not found."}
    except Exception as e:
        logger.error(f"Error deleting conversation {session_id}: {str(e)}")
        return {"status": "error", "message": f"Error deleting conversation: {str(e)}"}
    
@app.get("/health")
async def health_check():
    logger = logging.getLogger("health_check")
    logger.setLevel(logging.INFO)
    logger.info("Health check endpoint called")
    return {"status": "healthy", "framework": "Microsoft Agent Framework"}

# Teams endpoints (unchanged)
@app.get("/teams")
async def get_teams_api():
    try:
        teams = app.state.db.get_teams()
        return teams
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving teams: {str(e)}")

@app.get("/teams/{team_id}")
async def get_team_api(team_id: str):
    try:
        team = app.state.db.get_team(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        return team
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving team: {str(e)}")

@app.post("/teams")
async def create_team_api(team: dict):
    try:
        team["agents"] = AGENT_FRAMEWORK_DEFAULT_AGENTS
        response = app.state.db.create_team(team)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating team: {str(e)}")

@app.put("/teams/{team_id}")
async def update_team_api(team_id: str, team: dict):
    logger = logging.getLogger("update_team_api")
    logger.info(f"Updating team with ID: {team_id} and data: {team}")
    try:
        response = app.state.db.update_team(team_id, team)
        if "error" in response:
            logger.error(f"Error updating team: {response['error']}")
            raise HTTPException(status_code=404, detail=response["error"])
        return response
    except Exception as e:
        logger.error(f"Error updating team: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating team: {str(e)}")

@app.delete("/teams/{team_id}")
async def delete_team_api(team_id: str):
    try:
        response = app.state.db.delete_team(team_id)
        if "error" in response:
            raise HTTPException(status_code=404, detail=response["error"])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting team: {str(e)}")

@app.post("/inititalize-teams")
async def initialize_teams_api():
    try:
        msg = app.state.db.initialize_teams()
        msg = "Teams initialized successfully with Agent Framework."
        return {"status": "success", "message": msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing teams: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)