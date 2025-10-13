import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
PAGE_TITLE = "Dream Team Azure Agents"
PAGE_ICON = "🤖"

# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        align-self: flex-end;
        margin-left: 20%;
    }
    .agent-message {
        background-color: #f5f5f5;
        align-self: flex-start;
        margin-right: 20%;
    }
    .message-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #1976d2;
    }
    .message-content {
        white-space: pre-wrap;
    }
    .status-box {
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #4caf50;
        background-color: #e8f5e8;
        margin-bottom: 1rem;
    }
    .error-box {
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #f44336;
        background-color: #ffebee;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "user_id" not in st.session_state:
    st.session_state.user_id = "streamlit_user"
if "selected_agents" not in st.session_state:
    st.session_state.selected_agents = []
if "teams" not in st.session_state:
    st.session_state.teams = []

def get_default_agents():
    """Get the default agent configuration"""
    return [
        {
            "input_key": "0001",
            "type": "MagenticOne",
            "name": "Coder",
            "system_message": "",
            "description": "A helpful assistant that writes and executes code",
            "icon": "👨‍💻"
        },
        {
            "input_key": "0002",
            "type": "MagenticOne",
            "name": "WebSurfer", 
            "system_message": "",
            "description": "A web research specialist",
            "icon": "🏄‍♂️"
        },
        {
            "input_key": "0003",
            "type": "MagenticOne",
            "name": "FileSurfer",
            "system_message": "",
            "description": "A file and data exploration specialist", 
            "icon": "📂"
        }
    ]

def check_backend_health():
    """Check if the backend is healthy"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_agent_session(message: str, agents: List[Dict]):
    """Start a new agent session"""
    try:
        payload = {
            "content": message,
            "agents": json.dumps(agents),
            "user_id": st.session_state.user_id
        }
        response = requests.post(f"{BACKEND_URL}/start", json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to start session: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error starting session: {str(e)}")
        return None

def stream_chat_response(session_id: str, user_id: str):
    """Stream chat responses from the backend"""
    try:
        url = f"{BACKEND_URL}/chat-stream"
        params = {"session_id": session_id, "user_id": user_id}
        
        response = requests.get(url, params=params, stream=True, timeout=300)
        
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        try:
                            data = json.loads(line_text[6:])  # Remove 'data: ' prefix
                            yield data
                        except json.JSONDecodeError:
                            continue
        else:
            st.error(f"Failed to stream response: {response.status_code}")
    except Exception as e:
        st.error(f"Error streaming response: {str(e)}")

def get_agent_icon(source: str) -> str:
    """Get emoji icon for agent source"""
    icons = {
        "MagenticOneOrchestrator": "🎻",
        "CoderAgent": "👨‍💻", 
        "WebSurferAgent": "🏄‍♂️",
        "FileSurferAgent": "📂",
        "user": "👤",
        "workflow": "⚙️"
    }
    return icons.get(source, "🤖")

def render_message(message_data: Dict):
    """Render a chat message"""
    source = message_data.get("source", "unknown")
    content = message_data.get("content", "")
    msg_type = message_data.get("type", "")
    timestamp = message_data.get("time", "")
    
    icon = get_agent_icon(source)
    
    if source == "user":
        message_class = "user-message"
    else:
        message_class = "agent-message"
    
    # Format the message
    st.markdown(f"""
    <div class="chat-message {message_class}">
        <div class="message-header">
            {icon} {source} • {timestamp}
        </div>
        <div class="message-content">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Header
    st.title(f"{PAGE_ICON} {PAGE_TITLE}")
    st.subheader("Powered by Microsoft Agent Framework")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Backend health check
        health_status = check_backend_health()
        if health_status:
            st.markdown('<div class="status-box">✅ Backend Connected</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-box">❌ Backend Disconnected</div>', unsafe_allow_html=True)
            st.warning(f"Cannot connect to backend at {BACKEND_URL}")
        
        # User ID input
        user_id = st.text_input("User ID", value=st.session_state.user_id)
        st.session_state.user_id = user_id
        
        # Agent selection
        st.subheader("🤖 Select Agents")
        available_agents = get_default_agents()
        
        selected_agent_names = st.multiselect(
            "Choose agents for your team:",
            options=[agent["name"] for agent in available_agents],
            default=[agent["name"] for agent in available_agents[:2]],  # Default to first 2
            help="Select which agents to include in your conversation"
        )
        
        # Update selected agents
        st.session_state.selected_agents = [
            agent for agent in available_agents 
            if agent["name"] in selected_agent_names
        ]
        
        # Display selected agents
        if st.session_state.selected_agents:
            st.write("**Selected Team:**")
            for agent in st.session_state.selected_agents:
                st.write(f"{agent['icon']} {agent['name']} - {agent['description']}")
        
        # Session controls
        st.subheader("💬 Session")
        if st.button("🔄 New Session"):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()
        
        if st.session_state.session_id:
            st.write(f"**Session ID:** `{st.session_state.session_id[:12]}...`")
    
    # Main chat interface
    st.header("💬 Chat with Your Agent Team")
    
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            render_message(message)
    
    # Chat input
    if not st.session_state.selected_agents:
        st.warning("Please select at least one agent from the sidebar to start chatting.")
        return
    
    # User input
    user_input = st.chat_input("Ask your agent team anything...")
    
    if user_input:
        # Add user message to history
        user_message = {
            "source": "user",
            "content": user_input,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "user_message"
        }
        st.session_state.messages.append(user_message)
        
        # Start agent session if new
        if not st.session_state.session_id:
            session_response = start_agent_session(user_input, st.session_state.selected_agents)
            if session_response:
                st.session_state.session_id = session_response["response"]
            else:
                st.error("Failed to start agent session")
                return
        
        # Stream responses
        with st.spinner("🤖 Agent team is thinking..."):
            message_placeholder = st.empty()
            current_message = ""
            
            try:
                for response_data in stream_chat_response(st.session_state.session_id, st.session_state.user_id):
                    # Add to message history
                    st.session_state.messages.append(response_data)
                    
                    # Update display
                    message_placeholder.empty()
                    with message_placeholder.container():
                        render_message(response_data)
                    
                    # Check for completion
                    if response_data.get("stop_reason") == "completed":
                        break
                
            except Exception as e:
                st.error(f"Error during streaming: {str(e)}")
        
        # Rerun to update the UI
        st.rerun()

if __name__ == "__main__":
    main()