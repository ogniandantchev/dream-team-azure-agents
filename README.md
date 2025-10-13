[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/yaniv-vaknin-7a8324178/)

# Dream Team Azure Agents - Simplified

A simplified multi-agent AI system powered by **Microsoft Agent Framework**, **Streamlit**, and **Python Pulumi** - designed for easy partner demonstrations.

![Architecture](assets/architecture.png)

🎉 **March 2025**: Complete migration to simplified Python stack  
🎉 **February 2025**: Microsoft Agent Framework integration  
🎉 **January 2025**: Streamlit UI and Pulumi infrastructure
## 🚀 Key Simplifications

This version has been **completely reworked** to be much simpler and easier to present to partners:

### **Single Language Stack (Python Only)**
- ✅ **Backend**: Python with Microsoft Agent Framework (replaced Autogen)
- ✅ **Frontend**: Python Streamlit (replaced React/TypeScript)
- ✅ **Infrastructure**: Python Pulumi (replaced Bicep)

### **Modern AI Framework**
- ✅ **Microsoft Agent Framework**: Latest multi-agent orchestration
- ✅ **MagenticBuilder**: Advanced workflow orchestration  
- ✅ **Hosted Tools**: Code interpreter, web search, file operations
- ✅ **Real-time Streaming**: Better event handling and user experience

### **Partner Demo Ready**
- ✅ **Simple Setup**: Minimal configuration required
- ✅ **Clean UI**: Professional Streamlit interface
- ✅ **Live Demos**: Real-time agent conversations
- ✅ **Quick Deploy**: Azure Developer CLI compatible

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │ Agent Framework │    │ Azure Services  │
│   Frontend      │───▶│    Backend      │───▶│ (OpenAI, Cosmos)│
│   (Python)      │    │   (Python)      │    │    (Pulumi)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

# Key Features

Dream Team **Simplified** offers the following key features:

- **Microsoft Agent Framework**: Latest event-driven, asynchronous multi-agent system
- **Streamlit UI**: Clean, intuitive Python web interface - perfect for demos
- **Python Pulumi**: Infrastructure as Code with full programmatic control
- **Single line deployment**: `azd up` - from local development to Azure instantly
- **Secure code execution**: Azure Container Apps dynamic sessions for safe code execution
- **Managed Identities**: Built-in Azure authentication - no credential management needed
- **Real-time streaming**: Live agent conversations with immediate feedback

# Prerequisites

1. Install [Azure Developer CLI](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd)
2. Azure subscription access
3. Python 3.10+ (< 3.13)
4. [Pulumi CLI](https://www.pulumi.com/docs/get-started/install/) for infrastructure

# Quick Start

## 1. Clone the repository
```bash
git clone https://github.com/Azure-Samples/dream-team-azure-agents
cd dream-team-azure-agents
```

## 2. Login to your Azure account
```bash
azd auth login
```

## 3. Deploy with Azure Developer CLI
```bash
azd up
```

## 4. [Optional] Run locally for development

### Backend (Agent Framework)
```bash
cd backend_new
pip install -r requirements.txt
# Configure .env with Azure endpoints (created by azd up)
python main.py
```

### Frontend (Streamlit)
```bash
cd frontend_streamlit  
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Infrastructure (Pulumi)
```bash
cd infra_pulumi
pip install -r requirements.txt
pulumi stack init dev
pulumi config set principalId <your-principal-id>
pulumi up
```

## 5. [Optional] Ingest demo documents
```bash
cd backend_new
python aisearch.py
```

# 🤖 Available Agents

- **CoderAgent** 👨‍💻: Writes and executes Python code with secure sandboxing
- **WebSurferAgent** 🏄‍♂️: Performs web research and information gathering  
- **FileSurferAgent** 📂: Explores files and data structures intelligently
- **Custom Agents**: Easy to add domain-specific agents for any use case

# 🎯 Perfect for Partner Demos

### Why This Version is Demo-Friendly

1. **Single Language**: Everything is Python - easier to understand and modify
2. **Simple UI**: Streamlit provides clean, professional interface  
3. **Quick Setup**: Minimal configuration required
4. **Real-time**: Live agent conversations show AI capabilities
5. **Extensible**: Easy to add new agents for specific use cases
6. **Modern**: Uses latest Microsoft Agent Framework

### Demo Scenarios

- **Code Generation**: Show agents writing and executing code live
- **Research Tasks**: Demonstrate intelligent web search and analysis
- **Data Analysis**: File exploration and data processing capabilities
- **Multi-agent Collaboration**: Agents working together on complex tasks

# 📁 Project Structure

```
dream-team-azure-agents/
├── frontend_streamlit/          # 🎨 Streamlit frontend
│   ├── streamlit_app.py        # Main Streamlit app
│   ├── pyproject.toml          # Python dependencies
│   └── README.md               # Frontend documentation
├── backend_new/                 # 🤖 Agent Framework backend  
│   ├── main.py                 # FastAPI server
│   ├── agent_framework_helper.py # Agent orchestration
│   ├── pyproject.toml          # Python dependencies
│   └── README.md               # Backend documentation
├── infra_pulumi/               # ☁️ Pulumi infrastructure
│   ├── __main__.py             # Infrastructure code
│   ├── Pulumi.yaml             # Pulumi configuration
│   ├── pyproject.toml          # Python dependencies
│   └── README.md               # Infrastructure documentation
├── azure.yaml                  # Azure Developer CLI config
└── README.md                   # This file
```

# 🔄 Migration from Original

### What Changed

| Component | Before | After | Benefit |
|-----------|--------|-------|---------|
| Backend Framework | Autogen | Microsoft Agent Framework | Modern, supported, event-driven |
| Frontend | React/TypeScript | Streamlit/Python | Single language, simpler demos |
| Infrastructure | Bicep | Python Pulumi | Programmatic, testable, flexible |
| Complexity | High | **Low** | Easy to demo and customize |
| Languages | 3 (Python/JS/Bicep) | **1 (Python)** | Unified development experience |

### Backward Compatibility

The API endpoints remain compatible, so the migration preserves functionality while dramatically simplifying the architecture.
 

# Working Locally (Development Mode)

This simplified version uses Python for all components:

## Backend Development (Agent Framework)
```bash
cd backend_new
pip install -r requirements.txt
# Set up .env file with Azure service endpoints
uvicorn main:app --reload --port 8000
```

## Frontend Development (Streamlit)
```bash
cd frontend_streamlit
pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 8501
```

## Infrastructure Development (Pulumi)
```bash
cd infra_pulumi
pip install -r requirements.txt
pulumi stack select dev
pulumi preview  # See what will be deployed
pulumi up       # Deploy infrastructure
```

# 🤝 Contributing

This simplified version is designed for easy customization:

1. **Add New Agents**: Extend the agent configuration in `agent_framework_helper.py`
2. **Customize UI**: Modify the Streamlit app for specific demo needs
3. **Extend Infrastructure**: Add new Azure resources in the Pulumi code
4. **Enhanced Features**: Build on the simplified foundation

# Learn More

- [Microsoft Agent Framework Documentation](https://microsoft.github.io/agent-framework/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pulumi Azure Documentation](https://www.pulumi.com/docs/clouds/azure/)
- [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/)

---

**Perfect for partner demonstrations** - Simple, powerful, and built with modern Microsoft AI technologies. 🚀## Frontend (open a new terminal)
```bash
cd frontend
```
> Upadte the env variables in sample.env and rename to .env

## Run
```bash
npm run dev
```
If your app is ready, you can browse to (typically) http://localhost:8501 to see the app in action.
![Screenshot](./assets/application.png)

# Learn
Check these resources:
1. [Blogpost](https://techcommunity.microsoft.com/blog/Azure-AI-Services-blog/build-your-dream-team-with-autogen/4157961) - Build your dream team with Autogen
2. [Webinar](https://youtu.be/wB9gD9FkgNA?si=WU3H0QL37RCiTGvl) - More agents is all you need
