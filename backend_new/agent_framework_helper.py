import asyncio
import logging
import os
import tempfile
from typing import Optional, AsyncGenerator, Dict, Any, List
from dataclasses import dataclass

from agent_framework import (
    ChatAgent, MagenticBuilder, MagenticCallbackMode, MagenticCallbackEvent,
    MagenticOrchestratorMessageEvent, MagenticAgentDeltaEvent, MagenticAgentMessageEvent,
    MagenticFinalResultEvent, WorkflowCompletedEvent, WorkflowOutputEvent,
    HostedCodeInterpreterTool, HostedWebSearchTool, ai_function, MCPStdioTool
)
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
import random

load_dotenv()

def generate_session_name():
    '''Generate a unique session name based on random sci-fi words, e.g. quantum-cyborg-1234'''
    adjectives = [
        "quantum", "neon", "stellar", "galactic", "cyber", "holographic", "plasma", "nano", "hyper", "virtual",
        "cosmic", "interstellar", "lunar", "solar", "astro", "exo", "alien", "robotic", "synthetic", "digital",
        "futuristic", "parallel", "extraterrestrial", "transdimensional", "biomechanical", "cybernetic", "hologram",
        "metaphysical", "subatomic", "tachyon", "warp", "xeno", "zenith", "zerogravity", "antimatter", "darkmatter",
        "neural", "photon", "quantum", "singularity", "space-time", "stellar", "telepathic", "timetravel", "ultra",
        "virtualreality", "wormhole"
    ]
    nouns = [
        "cyborg", "android", "drone", "mech", "robot", "alien", "spaceship", "starship", "satellite", "probe",
        "astronaut", "cosmonaut", "galaxy", "nebula", "comet", "asteroid", "planet", "moon", "star", "quasar",
        "black-hole", "wormhole", "singularity", "dimension", "universe", "multiverse", "matrix", "simulation",
        "hologram", "avatar", "clone", "replicant", "cyberspace", "nanobot", "biobot", "exosuit", "spacesuit",
        "terraformer", "teleporter", "warpdrive", "hyperdrive", "stasis", "cryosleep", "fusion", "fission", "antigravity",
        "darkenergy", "neutrino", "tachyon", "photon"
    ]

    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    number = random.randint(1000, 9999)
    
    return f"{adjective}-{noun}-{number}"

@dataclass
class StreamingEvent:
    """Represents a streaming event from the Agent Framework workflow"""
    time: str
    session_id: str
    session_user: str
    event_type: str
    source: str
    content: str
    stop_reason: Optional[str] = None
    content_image: Optional[str] = None

class AgentFrameworkHelper:
    def __init__(self, logs_dir: str = None, save_screenshots: bool = False, run_locally: bool = False, user_id: str = None) -> None:
        """
        A helper class to interact with the Microsoft Agent Framework.
        Initialize Agent Framework instance.

        Args:
            logs_dir: Directory to store logs and downloads
            save_screenshots: Whether to save screenshots of web pages
            run_locally: Whether to run code execution locally or on Azure
            user_id: The user ID associated with this helper instance
        """
        self.logs_dir = logs_dir or os.getcwd()
        self.save_screenshots = save_screenshots
        self.run_locally = run_locally
        self.user_id = user_id

        self.max_rounds = 20
        self.max_time = 25 * 60
        self.max_stalls_before_replan = 3
        self.max_reset_count = 2

        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

        # Initialize Azure credential
        self.azure_credential = DefaultAzureCredential()

    async def initialize(self, agents, session_id=None) -> None:
        """
        Initialize the Agent Framework system, setting up agents and workflow.
        """
        # Generate session id
        if session_id is None:
            self.session_id = generate_session_name()
        else:
            self.session_id = session_id
            
        print(f"Session MODEL: gpt-4o using Agent Framework")

        # Create Azure OpenAI chat client
        self.chat_client = AzureOpenAIChatClient(
            model_id="gpt-4o",
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            credential=self.azure_credential,
        )

        # Set up agents
        self.agents = await self.setup_agents(agents, self.chat_client, self.logs_dir)
        print("Agents setup complete!")

    async def setup_agents(self, agents, chat_client, logs_dir):
        """Setup agents based on configuration"""
        agent_dict = {}
        
        for agent in agents:
            agent_name = agent["name"].lower().replace(" ", "_")
            
            if agent["type"] == "MagenticOne" and agent["name"] == "Coder":
                # Create coder agent with code interpreter
                coder = ChatAgent(
                    name="CoderAgent",
                    description="A helpful assistant that writes and executes code to process and analyze data.",
                    instructions="You solve questions using code. Please provide detailed analysis and computation process.",
                    chat_client=chat_client,
                    tools=[HostedCodeInterpreterTool()],
                )
                agent_dict["coder"] = coder
                print("Coder agent added!")

            elif agent["type"] == "MagenticOne" and agent["name"] == "WebSurfer":
                # Create web surfer agent with web search
                web_surfer = ChatAgent(
                    name="WebSurferAgent",
                    description="Specialist in web research and information gathering",
                    instructions="You are a web researcher. You find information from the internet without additional computation or quantitative analysis.",
                    chat_client=chat_client,
                    tools=[HostedWebSearchTool()],
                )
                agent_dict["websurfer"] = web_surfer
                print("WebSurfer agent added!")

            elif agent["type"] == "MagenticOne" and agent["name"] == "FileSurfer":
                # Create file surfer agent
                @ai_function
                def read_file(file_path: str) -> str:
                    """Read the contents of a file."""
                    try:
                        full_path = os.path.join(logs_dir, "data", file_path)
                        with open(full_path, 'r', encoding='utf-8') as f:
                            return f.read()
                    except Exception as e:
                        return f"Error reading file: {str(e)}"

                @ai_function 
                def list_files(directory: str = ".") -> str:
                    """List files in a directory."""
                    try:
                        full_path = os.path.join(logs_dir, "data", directory)
                        files = os.listdir(full_path)
                        return "\n".join(files)
                    except Exception as e:
                        return f"Error listing files: {str(e)}"

                file_surfer = ChatAgent(
                    name="FileSurferAgent",
                    description="Specialist in file operations and data exploration",
                    instructions="You are a file explorer. You can read files and list directories to help understand data structures.",
                    chat_client=chat_client,
                    tools=[read_file, list_files],
                )
                agent_dict["filesurfer"] = file_surfer
                print("FileSurfer agent added!")

            elif agent["type"] == "Custom":
                # Create custom agent
                custom_agent = ChatAgent(
                    name=f"{agent['name']}Agent",
                    description=agent.get("description", "A custom specialized agent"),
                    instructions=agent.get("system_message", "You are a helpful assistant."),
                    chat_client=chat_client,
                )
                agent_dict[agent_name] = custom_agent
                print(f'{agent["name"]} (custom) added!')

            elif agent["type"] == "CustomMCP":
                # Create MCP agent with communication tools
                @ai_function
                def send_email(to: str, subject: str, body: str) -> str:
                    """Send an email using Azure Communication Services."""
                    # Implementation would use Azure Communication Services
                    return f"Email sent to {to} with subject: {subject}"

                mcp_agent = ChatAgent(
                    name=f"{agent['name']}Agent",
                    description=agent.get("description", "A custom MCP agent with communication capabilities"),
                    instructions=agent.get("system_message", "You are a helpful assistant.") + f"\n\nIn case of email use this address as TO: {self.user_id}",
                    chat_client=chat_client,
                    tools=[send_email],
                )
                agent_dict[agent_name] = mcp_agent
                print(f'{agent["name"]} (custom MCP) added!')

            elif agent["type"] == "RAG":
                # Create RAG agent with Azure AI Search
                @ai_function
                def search_knowledge_base(query: str) -> str:
                    """Search the knowledge base for relevant information."""
                    # Implementation would use Azure AI Search
                    return f"Knowledge base search results for: {query}"

                rag_agent = ChatAgent(
                    name=f"{agent['name']}Agent",
                    description=agent.get("description", "A RAG agent with knowledge base access"),
                    instructions="You are a knowledge assistant with access to specialized information through search.",
                    chat_client=chat_client,
                    tools=[search_knowledge_base],
                )
                agent_dict[agent_name] = rag_agent
                print(f'{agent["name"]} (RAG) added!')

        return agent_dict

    async def create_workflow(self, task: str):
        """Create and configure the Magentic workflow"""
        
        # Store streaming events for later retrieval
        self.streaming_events = []
        
        # Event handling for streaming
        async def on_event(event: MagenticCallbackEvent) -> None:
            if isinstance(event, MagenticOrchestratorMessageEvent):
                self.streaming_events.append(StreamingEvent(
                    time=self._get_current_time(),
                    session_id=self.session_id,
                    session_user=self.user_id,
                    event_type="orchestrator",
                    source="MagenticOneOrchestrator",
                    content=getattr(event.message, 'text', ''),
                ))

            elif isinstance(event, MagenticAgentDeltaEvent):
                self.streaming_events.append(StreamingEvent(
                    time=self._get_current_time(),
                    session_id=self.session_id,
                    session_user=self.user_id,
                    event_type="agent_delta", 
                    source=event.agent_id,
                    content=event.text,
                ))

            elif isinstance(event, MagenticAgentMessageEvent):
                msg = event.message
                if msg is not None:
                    self.streaming_events.append(StreamingEvent(
                        time=self._get_current_time(),
                        session_id=self.session_id,
                        session_user=self.user_id,
                        event_type="agent_message",
                        source=event.agent_id,
                        content=msg.text or '',
                    ))

            elif isinstance(event, MagenticFinalResultEvent):
                self.streaming_events.append(StreamingEvent(
                    time=self._get_current_time(),
                    session_id=self.session_id,
                    session_user=self.user_id,
                    event_type="final_result",
                    source="workflow",
                    content=event.message.text if event.message else '',
                    stop_reason="completed"
                ))

        # Build workflow
        workflow_builder = MagenticBuilder()
        
        # Add available agents
        workflow_builder = workflow_builder.participants(**self.agents)
        
        # Configure workflow with manager
        workflow = (workflow_builder
                   .on_event(on_event, mode=MagenticCallbackMode.STREAMING)
                   .with_standard_manager(
                       chat_client=self.chat_client,
                       max_round_count=self.max_rounds,
                       max_stall_count=self.max_stalls_before_replan,
                       max_reset_count=self.max_reset_count,
                   )
                   .build())
        
        return workflow

    def main(self, task):
        """Create and return the workflow stream for a given task"""
        async def _event_stream():
            workflow = await self.create_workflow(task)
            self.streaming_events = []  # Reset events
            
            async for event in workflow.run_stream(task):
                # Yield any accumulated streaming events
                for streaming_event in self.streaming_events:
                    yield streaming_event
                self.streaming_events = []
                
                if isinstance(event, WorkflowOutputEvent):
                    yield StreamingEvent(
                        time=self._get_current_time(),
                        session_id=self.session_id,
                        session_user=self.user_id,
                        event_type="workflow_output",
                        source="workflow",
                        content=str(event.data),
                        stop_reason="completed"
                    )
                elif isinstance(event, WorkflowCompletedEvent):
                    yield StreamingEvent(
                        time=self._get_current_time(),
                        session_id=self.session_id,
                        session_user=self.user_id,
                        event_type="workflow_completed",
                        source="workflow", 
                        content=str(getattr(event, 'data', '')),
                        stop_reason="completed"
                    )
                    
        return _event_stream(), None  # Return generator and None for cancellation_token compatibility

    def _get_current_time(self):
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

async def main(agents, task, run_locally) -> None:
    """Main function for testing the Agent Framework helper"""
    
    agent_helper = AgentFrameworkHelper(logs_dir=".", run_locally=run_locally)
    await agent_helper.initialize(agents)

    workflow = await agent_helper.create_workflow(task)
    
    try:
        async for event in workflow.run_stream(task):
            if isinstance(event, WorkflowCompletedEvent):
                print(f"Final result: {event.data}")
                break
            elif isinstance(event, WorkflowOutputEvent):
                print(f"Output: {event.data}")
            else:
                print(f"Event: {type(event).__name__}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":   
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
            "input_key":"0004",
            "type":"MagenticOne",
            "name":"WebSurfer",
            "system_message":"",
            "description":"",
            "icon":"🏄‍♂️"
        },
    ]
    
    import argparse
    parser = argparse.ArgumentParser(description="Run AgentFrameworkHelper with specified task and run_locally option.")
    parser.add_argument("--task", "-t", type=str, required=True, help="The task to run, e.g. 'How much taxes elon musk paid?'")
    parser.add_argument("--run_locally", action="store_true", help="Run locally if set")
    
    args = parser.parse_args()

    asyncio.run(main(AGENT_FRAMEWORK_DEFAULT_AGENTS, args.task, args.run_locally))