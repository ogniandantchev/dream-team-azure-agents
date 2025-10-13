## Pulumi Infrastructure

This directory contains the Python Pulumi infrastructure code that replaces the Bicep templates.

### Key Benefits Over Bicep

1. **Single Language**: Python throughout the entire stack
2. **Rich Ecosystem**: Access to Python libraries and tooling
3. **Type Safety**: Better IntelliSense and error checking
4. **Programmatic**: Loops, conditionals, and functions for complex logic
5. **Testing**: Unit testing infrastructure code with pytest
6. **State Management**: Built-in state management and drift detection

### Resources Created

- **Resource Group**: Container for all resources
- **Container Apps Environment**: Hosting environment for backend
- **Container Registry**: Store Docker images
- **Azure OpenAI**: GPT-4o and embedding models
- **Cosmos DB**: Serverless NoSQL database
- **AI Search**: Vector search capabilities
- **Key Vault**: Secrets management
- **Storage Account**: Blob storage
- **Log Analytics**: Monitoring and logging
- **Virtual Network**: Network isolation
- **Managed Identity**: Secure authentication
- **Communication Services**: Email capabilities
- **Static Web App**: Frontend hosting

### Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize Pulumi
pulumi stack init dev

# Configure required settings
pulumi config set principalId <your-principal-id>
pulumi config set environmentName dev
pulumi config set location eastus

# Preview changes
pulumi preview

# Deploy infrastructure
pulumi up

# Get outputs
pulumi stack output backend_url
pulumi stack output frontend_url
```

### Configuration

Required configuration:
- `principalId`: Azure AD principal ID for role assignments
- `environmentName`: Environment name (dev, staging, prod)
- `location`: Azure region (default: eastus)

### Outputs

The stack exports key endpoints and configuration values:
- `backend_url`: Container App backend URL
- `frontend_url`: Static Web App frontend URL  
- `azure_openai_endpoint`: OpenAI service endpoint
- `cosmos_db_uri`: Cosmos DB connection endpoint
- `ai_search_endpoint`: AI Search service endpoint
- `container_registry_login_server`: Container registry URL
- `key_vault_uri`: Key Vault endpoint
- `managed_identity_client_id`: Managed identity for authentication