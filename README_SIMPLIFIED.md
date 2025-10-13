# Dream Team Azure Agents - Simplified

A simplified multi-agent AI system powered by Microsoft Agent Framework, Streamlit, and Python Pulumi - designed for easy partner demonstrations.

## 🚀 Key Simplifications

This version has been reworked to be much simpler and easier to present to partners:

### 1. **Single Language Stack (Python)**
- ✅ **Backend**: Python with Microsoft Agent Framework (replacing Autogen)
- ✅ **Frontend**: Python Streamlit (replacing React/TypeScript)
- ✅ **Infrastructure**: Python Pulumi (replacing Bicep)

### 2. **Modern AI Framework**
- ✅ **Microsoft Agent Framework**: Latest multi-agent orchestration
- ✅ **MagenticBuilder**: Advanced workflow orchestration
- ✅ **Hosted Tools**: Code interpreter, web search, file operations
- ✅ **Real-time Streaming**: Better event handling and user experience

### 3. **Simplified UI**
- ✅ **Streamlit Interface**: Clean, intuitive chat interface
- ✅ **Real-time Updates**: Live agent conversations
- ✅ **Easy Configuration**: Simple agent selection and team management
- ✅ **Status Monitoring**: Backend health and session tracking

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │ Agent Framework │    │ Azure Services  │
│   Frontend      │───▶│    Backend      │───▶│ (OpenAI, Cosmos)│
│   (Python)      │    │   (Python)      │    │    (Pulumi)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Components

1. **Frontend** (`frontend_streamlit/`): 
   - Streamlit web app with chat interface
   - Real-time agent communication
   - Simple configuration and monitoring

2. **Backend** (`backend_new/`):
   - Microsoft Agent Framework with MagenticBuilder
   - Multi-agent orchestration (Coder, WebSurfer, FileSurfer)
   - FastAPI with streaming endpoints

3. **Infrastructure** (`infra_pulumi/`):
   - Python Pulumi for Azure resource management
   - Container Apps, OpenAI, Cosmos DB, AI Search
   - Managed Identity and secure authentication

## 🛠️ Quick Start

### Prerequisites
- Python 3.10+
- Azure CLI
- Azure subscription
- Pulumi CLI

### 1. Deploy Infrastructure
```bash
cd infra_pulumi
pip install -r requirements.txt
pulumi stack init dev
pulumi config set principalId <your-principal-id>
pulumi up
```

### 2. Run Backend Locally
```bash
cd backend_new
pip install -r requirements.txt
# Configure .env with Azure endpoints
python main.py
```

### 3. Run Frontend Locally
```bash
cd frontend_streamlit
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### 4. Deploy with Azure Developer CLI
```bash
azd auth login
azd up
```

## 🤖 Available Agents

- **CoderAgent** 👨‍💻: Writes and executes Python code
- **WebSurferAgent** 🏄‍♂️: Performs web research and searches
- **FileSurferAgent** 📂: Explores files and data structures
- **Custom Agents**: Easy to add domain-specific agents

## 🎯 Perfect for Partner Demos

### Why This Version is Demo-Friendly

1. **Single Language**: Everything is Python - easier to understand and modify
2. **Simple UI**: Streamlit provides clean, professional interface
3. **Quick Setup**: Minimal configuration required
4. **Real-time**: Live agent conversations show AI capabilities
5. **Extensible**: Easy to add new agents for specific use cases
6. **Modern**: Uses latest Microsoft Agent Framework

### Demo Scenarios

- **Code Generation**: Show agents writing and executing code
- **Research Tasks**: Demonstrate web search and analysis
- **Data Analysis**: File exploration and data processing
- **Multi-agent Collaboration**: Agents working together on complex tasks

## 📁 Project Structure

```
dream-team-azure-agents/
├── frontend_streamlit/          # Streamlit frontend
│   ├── streamlit_app.py        # Main Streamlit app
│   ├── pyproject.toml          # Python dependencies
│   └── README.md               # Frontend documentation
├── backend_new/                 # Agent Framework backend  
│   ├── main.py                 # FastAPI server
│   ├── agent_framework_helper.py # Agent orchestration
│   ├── pyproject.toml          # Python dependencies
│   └── README.md               # Backend documentation
├── infra_pulumi/               # Pulumi infrastructure
│   ├── __main__.py             # Infrastructure code
│   ├── Pulumi.yaml             # Pulumi configuration
│   ├── pyproject.toml          # Python dependencies
│   └── README.md               # Infrastructure documentation
├── azure.yaml                  # Azure Developer CLI config
└── README.md                   # This file
```

## 🔄 Migration from Original

### What Changed

| Component | Before | After | Benefit |
|-----------|--------|-------|---------|
| Backend Framework | Autogen | Microsoft Agent Framework | Modern, supported framework |
| Frontend | React/TypeScript | Streamlit/Python | Single language, simpler |
| Infrastructure | Bicep | Python Pulumi | Programmatic, testable |
| Complexity | High | Low | Easy to demo and modify |

### Backward Compatibility

The API endpoints remain compatible, so the migration preserves functionality while simplifying the architecture.

## 🤝 Contributing

This simplified version is designed for easy customization:

1. **Add New Agents**: Extend the agent configuration in `agent_framework_helper.py`
2. **Customize UI**: Modify the Streamlit app for specific demo needs
3. **Extend Infrastructure**: Add new Azure resources in the Pulumi code
4. **Enhanced Features**: Build on the simplified foundation

## 📞 Support

For questions about the simplified architecture or demo setup, please refer to the individual component READMEs or create an issue.

---

**Perfect for partner demonstrations** - Simple, powerful, and built with modern Microsoft AI technologies.