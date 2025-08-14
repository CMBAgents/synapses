# CMB Agent MCP Server

This MCP (Model Context Protocol) server provides tools to interact with your cmbagent-info app, specifically designed for the astronomy chatbot and other features available at [https://cmbchat.cloud](https://cmbchat.cloud).

## Features

The MCP server provides the following tools:

- **`list_programs`** - List all available astronomy and finance programs
- **`chat_with_astronomy`** - Chat with the astronomy chatbot using specific programs
- **`get_program_context`** - Retrieve context/documentation for specific programs
- **`check_service_health`** - Check the health status of the CMB Agent service
- **`search_astronomy_libraries`** - Search through available astronomy libraries
- **`get_astronomy_leaderboard`** - Get astronomy leaderboard data
- **`get_finance_leaderboard`** - Get finance leaderboard data

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements_mcp.txt
```

2. Make sure you have the MCP Python package installed:
```bash
pip install mcp
```

## Usage

### Running the MCP Server

#### Option 1: Direct execution
```bash
python mcp_cmbagent.py stdio
```

#### Option 2: With custom base URL
```bash
python mcp_cmbagent.py stdio --base-url http://localhost:3000
```

#### Option 3: SSE transport (for web-based clients)
```bash
python mcp_cmbagent.py sse --base-url http://localhost:3000
```

### Testing the Server

Run the test script to verify everything works:
```bash
python test_mcp_cmbagent.py
```

### Integration with AutoGen

You can integrate this MCP server with AutoGen agents:

```python
from autogen.mcp import create_toolkit
from autogen import ConversableAgent

# Create MCP toolkit
toolkit = create_toolkit(
    mcp_server_path="mcp_cmbagent.py",
    mcp_server_args=["stdio"]
)

# Create an agent with MCP tools
agent = ConversableAgent(
    name="cmb_agent",
    llm_config={"config_list": [{"model": "gpt-4"}]}
)

# Register MCP tools
toolkit.register_for_llm(agent)
toolkit.register_for_execution(agent)
```

### Example MCP Client Usage

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_cmbagent.py", "stdio"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # List available programs
            result = await session.call_tool("list_programs", {})
            print(f"Programs: {result.content}")
            
            # Chat with astronomy chatbot
            result = await session.call_tool("chat_with_astronomy", {
                "message": "What is python-skyfield?",
                "program_id": "skyfielders-python-skyfield"
            })
            print(f"Response: {result.content}")

asyncio.run(main())
```

## Configuration

The server can be configured using the `mcp_cmbagent_config.json` file or by passing command-line arguments:

- **`--base-url`**: Base URL for the CMB Agent service (default: https://cmbchat.cloud)
- **`transport`**: Transport mode - `stdio` or `sse`

## Available Programs

The server provides access to various astronomy and finance programs including:

- **python-skyfield** - Astrophysics library with 1570 stars
- **astrometry.net** - Astrophysics library with 750 stars  
- **astroquery** - Astrophysics library with 739 stars
- **einsteinpy** - Astrophysics library with 650 stars
- **lightkurve** - Astrophysics library with 459 stars
- And many more...

## API Endpoints

The server interacts with these endpoints from your cmbagent-info app:

- `/api/unified-chat` - Main chat endpoint
- `/api/context/{programId}` - Program context/documentation
- `/api/health` - Service health check
- `/astronomy/leaderboard` - Astronomy leaderboard
- `/finance/leaderboard` - Finance leaderboard

## Error Handling

The server includes comprehensive error handling for:
- Network connectivity issues
- Invalid program IDs
- Service unavailability
- Malformed responses

## Development

To extend the server with new tools:

1. Add new methods to the `CMBAgentClient` class
2. Create corresponding `@mcp.tool()` decorated functions
3. Update the test script to include new functionality

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure all dependencies are installed
2. **Connection refused**: Verify the base URL is correct and accessible
3. **Tool not found**: Check that the MCP server is running with the correct transport mode

### Debug Mode

Enable debug logging by setting the `PYTHONPATH` environment variable:
```bash
export PYTHONPATH=.
python mcp_cmbagent.py stdio
```

## License

This MCP server is part of the cmbagent-info project and follows the same license terms.
