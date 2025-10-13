## Agent Framework Backend

This is the migrated backend using Microsoft Agent Framework instead of Autogen.

### Key Changes

1. **Dependencies**: 
   - Replaced `autogen-agentchat`, `autogen-ext`, `autogen-core` with `agent-framework[azure]`
   - Updated to use modern Microsoft Agent Framework

2. **Agent Architecture**:
   - `MagenticOneGroupChat` → `MagenticBuilder` workflow
   - `AssistantAgent` → `ChatAgent` 
   - `AzureOpenAIChatCompletionClient` → `AzureOpenAIChatClient`
   - Hosted tools: `HostedCodeInterpreterTool`, `HostedWebSearchTool`

3. **Streaming**:
   - Updated streaming to use Agent Framework's event system
   - Improved callback handling for real-time updates

4. **Workflow Management**:
   - Modern workflow orchestration with typed data flow
   - Better error handling and state management

### Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

The API endpoints remain the same for backwards compatibility with the frontend.