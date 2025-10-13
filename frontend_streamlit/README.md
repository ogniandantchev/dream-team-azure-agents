## Streamlit Frontend

This is the simplified Streamlit frontend that replaces the React/TypeScript frontend.

### Key Features

1. **Simplified UI**: Clean, intuitive interface perfect for partner demos
2. **Real-time Chat**: Streaming conversations with AI agents
3. **Agent Configuration**: Easy agent selection and team management
4. **Conversation History**: Access to previous chat sessions
5. **Status Monitoring**: Real-time backend health and session status

### Key Benefits Over React Frontend

- **Single Language**: Pure Python, no JavaScript/TypeScript
- **Rapid Development**: Streamlit handles UI complexity
- **Easy Customization**: Simple to modify for specific demos
- **Built-in Components**: Chat interface, forms, and layouts included
- **Deployment**: Easy to deploy and share

### Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Configuration

Copy `.env.example` to `.env` and configure:
- `BACKEND_URL`: URL of the Agent Framework backend
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint

### Features

- **Chat Interface**: Send messages and receive real-time agent responses
- **Agent Selection**: Choose which agents to include in conversations
- **Team Management**: Use predefined agent teams
- **Conversation History**: Access previous chat sessions
- **Status Dashboard**: Monitor agent activity and backend health