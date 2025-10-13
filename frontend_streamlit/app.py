import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="Dream Team Azure Agents",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 10%;
    }
    .agent-message {
        background-color: #f5f5f5;
        margin-right: 10%;
    }
    .agent-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def get_agent_icon(agent_name: str) -> str:
    """Get icon for agent based on name"""
    icons = {
        "MagenticOneOrchestrator": "🎻",
        "WebSurferAgent": "🏄‍♂️", 
        "CoderAgent": "👨‍💻",
        "FileSurferAgent": "📂",
        "user": "👤",
        "workflow": "⚙️"
    }
    return icons.get(agent_name, "🤖")

def format_message(message: Dict, is_user: bool = False) -> str:
    """Format message for display"""
    if is_user:
        return f"""
        <div class="chat-message user-message">
            <span class="agent-icon">👤</span>
            <strong>You:</strong> {message.get('content', '')}
        </div>
        """
    else:
        icon = get_agent_icon(message.get('source', ''))
        source = message.get('source', 'Agent')
        content = message.get('content', '')
        
        return f"""
        <div class="chat-message agent-message">
            <span class="agent-icon">{icon}</span>
            <strong>{source}:</strong> {content}
        </div>
        """

class StreamlitAgentChat:
    def __init__(self):
        self.session_id = None
        self.user_id = "streamlit_user"
        
    def initialize_session(self):
        """Initialize session state"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "session_id" not in st.session_state:
            st.session_state.session_id = None
        if "is_streaming" not in st.session_state:
            st.session_state.is_streaming = False
        if "selected_agents" not in st.session_state:
            st.session_state.selected_agents = self.get_default_agents()
    
    def get_default_agents(self) -> List[Dict]:
        """Get default agent configuration"""
        return [
            {
                "input_key": "0001",
                "type": "MagenticOne",
                "name": "Coder",
                "system_message": "",
                "description": "Code execution and analysis agent",
                "icon": "👨‍💻"
            },
            {
                "input_key": "0002",
                "type": "MagenticOne", 
                "name": "WebSurfer",
                "system_message": "",
                "description": "Web research and information gathering agent",
                "icon": "🏄‍♂️"
            },
            {
                "input_key": "0003",
                "type": "MagenticOne",
                "name": "FileSurfer", 
                "system_message": "",
                "description": "File exploration and data analysis agent",
                "icon": "📂"
            }
        ]
    
    def start_session(self, task: str) -> Optional[str]:
        """Start a new agent session"""
        try:
            payload = {
                "content": task,
                "agents": json.dumps(st.session_state.selected_agents),
                "user_id": self.user_id
            }
            
            response = requests.post(f"{BACKEND_URL}/start", json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response")  # This is the session_id
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error starting session: {str(e)}")
            return None
    
    def stream_responses(self, session_id: str):
        """Stream responses from the agent"""
        try:
            url = f"{BACKEND_URL}/chat-stream"
            params = {"session_id": session_id, "user_id": self.user_id}
            
            with requests.get(url, params=params, stream=True) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])  # Remove 'data: ' prefix
                                yield data
                            except json.JSONDecodeError:
                                continue
                                
        except requests.exceptions.RequestException as e:
            st.error(f"Error streaming responses: {str(e)}")
            yield None
    
    def get_teams(self) -> List[Dict]:
        """Get available teams"""
        try:
            response = requests.get(f"{BACKEND_URL}/teams")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching teams: {str(e)}")
            return []
    
    def get_conversations(self) -> List[Dict]:
        """Get user conversations"""
        try:
            payload = {"user_id": self.user_id}
            response = requests.post(f"{BACKEND_URL}/conversations/user", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching conversations: {str(e)}")
            return []

def main():
    st.title("🤖 Dream Team Azure Agents")
    st.subheader("Powered by Microsoft Agent Framework")
    
    # Initialize the chat system
    chat = StreamlitAgentChat()
    chat.initialize_session()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Agent selection
        st.subheader("🤖 Agents")
        available_agents = chat.get_default_agents()
        
        for i, agent in enumerate(available_agents):
            key = f"agent_{agent['input_key']}"
            enabled = st.checkbox(
                f"{agent['icon']} {agent['name']}", 
                value=True,
                key=key,
                help=agent['description']
            )
            
            if not enabled:
                st.session_state.selected_agents = [
                    a for a in st.session_state.selected_agents 
                    if a['input_key'] != agent['input_key']
                ]
            elif agent not in st.session_state.selected_agents:
                st.session_state.selected_agents.append(agent)
        
        st.divider()
        
        # Teams section
        st.subheader("👥 Teams")
        teams = chat.get_teams()
        if teams:
            team_names = [team.get('name', 'Unnamed Team') for team in teams]
            selected_team = st.selectbox("Select Team", ["Default"] + team_names)
            
            if selected_team != "Default":
                team_idx = team_names.index(selected_team)
                team_agents = teams[team_idx].get('agents', [])
                if team_agents:
                    st.session_state.selected_agents = team_agents
        
        st.divider()
        
        # Conversation history
        st.subheader("💬 Recent Conversations")
        conversations = chat.get_conversations()
        if conversations:
            for conv in conversations[:5]:  # Show last 5 conversations
                if st.button(f"📝 {conv.get('messages', [{}])[0].get('content', 'No content')[:30]}..."):
                    st.session_state.session_id = conv.get('session_id')
                    st.session_state.messages = conv.get('messages', [])
                    st.experimental_rerun()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.experimental_rerun()
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Display chat messages
        if st.session_state.messages:
            st.subheader("💬 Conversation")
            
            for message in st.session_state.messages:
                if message.get('role') == 'user':
                    st.markdown(format_message(message, is_user=True), unsafe_allow_html=True)
                else:
                    st.markdown(format_message(message, is_user=False), unsafe_allow_html=True)
        
        # Message input
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_area(
                "Enter your message:",
                placeholder="Ask the agents to help you with a task...",
                height=100,
                key="user_input"
            )
            submitted = st.form_submit_button("Send 🚀", use_container_width=True)
        
        # Process user input
        if submitted and user_input and not st.session_state.is_streaming:
            # Add user message to chat
            user_message = {
                "role": "user",
                "content": user_input,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.messages.append(user_message)
            
            # Start new session
            st.session_state.is_streaming = True
            session_id = chat.start_session(user_input)
            
            if session_id:
                st.session_state.session_id = session_id
                
                # Create placeholder for streaming responses
                response_placeholder = st.empty()
                current_response = ""
                
                # Stream responses
                for response_data in chat.stream_responses(session_id):
                    if response_data:
                        content = response_data.get('content', '')
                        source = response_data.get('source', 'Agent')
                        
                        if content:
                            # Update current response
                            current_response += f"\n**{source}:** {content}"
                            response_placeholder.markdown(current_response)
                            
                            # Add to messages
                            agent_message = {
                                "role": "assistant",
                                "content": content,
                                "source": source,
                                "time": response_data.get('time', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            }
                            st.session_state.messages.append(agent_message)
                
                st.session_state.is_streaming = False
                st.experimental_rerun()
    
    with col2:
        # Status and info panel
        st.subheader("📊 Status")
        
        if st.session_state.session_id:
            st.success(f"Session: {st.session_state.session_id[:8]}...")
        else:
            st.info("No active session")
        
        if st.session_state.is_streaming:
            st.warning("🔄 Agents are working...")
        else:
            st.info("✅ Ready")
        
        st.subheader("🎯 Active Agents")
        for agent in st.session_state.selected_agents:
            st.write(f"{agent['icon']} {agent['name']}")
        
        st.subheader("ℹ️ About")
        st.markdown("""
        This demo showcases Microsoft Agent Framework with:
        - **Magentic Orchestration**: Intelligent agent coordination
        - **Hosted Tools**: Code execution and web search
        - **Real-time Streaming**: Live conversation updates
        - **Azure Integration**: Powered by Azure OpenAI
        """)
        
        # Health check
        try:
            health_response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if health_response.status_code == 200:
                health_data = health_response.json()
                st.success(f"✅ Backend: {health_data.get('framework', 'Connected')}")
            else:
                st.error("❌ Backend: Unhealthy")
        except:
            st.error("❌ Backend: Disconnected")

if __name__ == "__main__":
    main()