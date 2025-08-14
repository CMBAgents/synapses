import argparse
import requests
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("CMBAgentServer")

# Default configuration
DEFAULT_BASE_URL = "http://localhost:3000"
DEFAULT_PROGRAM_ID = "skyfielders-python-skyfield"

class CMBAgentClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def get_programs(self) -> List[Dict[str, Any]]:
        """Get available programs from the config."""
        try:
            # Try to fetch from the main page or config endpoint
            response = self.session.get(f"{self.base_url}/api/context")
            if response.status_code == 200:
                return response.json()
            else:
                # Fallback to hardcoded programs based on config.json
                return [
                    {
                        "id": "skyfielders-python-skyfield",
                        "name": "python-skyfield",
                        "description": "skyfielders/python-skyfield - Astrophysics library with 150 stars"
                    },
                    {
                        "id": "dstndstn-astrometry-net",
                        "name": "astrometry.net",
                        "description": "dstndstn/astrometry.net - Astrophysics library with 750 stars"
                    },
                    {
                        "id": "astropy-astroquery",
                        "name": "astroquery",
                        "description": "astropy/astroquery - Astrophysics library with 739 stars"
                    }
                ]
        except Exception as e:
            print(f"Error fetching programs: {e}")
            return []
    
    def chat_with_program(self, program_id: str, message: str) -> Dict[str, Any]:
        """Send a chat message to a specific program using the default model."""
        try:
            payload = {
                "programId": program_id,
                "messages": [{"role": "user", "content": message}],
                "stream": True,  # Set to True to match the model configuration
                "modelId": "deepseek/deepseek-chat-v3-0324",  # Explicitly set the default model
                "credentials": {
                    "deepseek/deepseek-chat-v3-0324": {
                        "apiKey": os.environ.get("OPEN_ROUTER_KEY", "")
                    }
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/unified-chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                # Handle streaming response
                if response.headers.get('Content-Type', '').startswith('text/event-stream'):
                    # This is a streaming response, consume it
                    content = ""
                    for line in response.text.split('\n'):
                        if line.startswith('data: '):
                            data = line[6:]  # Remove 'data: ' prefix
                            if data == '[DONE]':
                                break
                            try:
                                chunk = json.loads(data)
                                if 'choices' in chunk and chunk['choices'] and 'delta' in chunk['choices'][0]:
                                    delta_content = chunk['choices'][0]['delta'].get('content', '')
                                    if delta_content:
                                        content += delta_content
                            except json.JSONDecodeError:
                                continue
                    
                    return {"content": content}
                else:
                    # Non-streaming response
                    return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def get_context(self, program_id: str) -> str:
        """Get the context for a specific program."""
        try:
            response = self.session.get(f"{self.base_url}/api/context/{program_id}")
            if response.status_code == 200:
                return response.text
            else:
                return f"Error fetching context: HTTP {response.status_code}"
        except Exception as e:
            return f"Error fetching context: {str(e)}"
    
    def get_health(self) -> Dict[str, Any]:
        """Check the health of the CMB Agent service."""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

# Initialize the client
client = CMBAgentClient()

@mcp.tool()
def list_programs() -> List[Dict[str, str]]:
    """List all available programs in the CMB Agent system."""
    programs = client.get_programs()
    return [{"id": p["id"], "name": p["name"], "description": p["description"]} for p in programs]

@mcp.tool()
def chat_with_astronomy(message: str, program_id: str = DEFAULT_PROGRAM_ID) -> Dict[str, Any]:
    """Chat with the astronomy chatbot using the default model (deepseek via OpenRouter)."""
    # Always use the default model - no need to pass model_id
    return client.chat_with_program(program_id, message)

@mcp.tool()
def get_program_context(program_id: str) -> str:
    """Get the context/documentation for a specific program."""
    return client.get_context(program_id)

@mcp.tool()
def check_service_health() -> Dict[str, Any]:
    """Check the health status of the CMB Agent service."""
    return client.get_health()

@mcp.tool()
def search_astronomy_libraries(query: str) -> List[Dict[str, str]]:
    """Search through available astronomy libraries."""
    programs = client.get_programs()
    query_lower = query.lower()
    
    results = []
    for program in programs:
        if (query_lower in program["name"].lower() or 
            query_lower in program["description"].lower() or
            query_lower in program["id"].lower()):
            results.append({
                "id": program["id"],
                "name": program["name"],
                "description": program["description"]
            })
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CMB Agent MCP Server")
    parser.add_argument("transport", choices=["stdio"], help="Transport mode")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL for CMB Agent service")
    parser.add_argument("--openrouter-key", help="OpenRouter API key for authentication")
    args = parser.parse_args()
    
    # Update client with custom base URL if provided
    if args.base_url != DEFAULT_BASE_URL:
        client = CMBAgentClient(args.base_url)
    
    # Set OpenRouter API key if provided
    if args.openrouter_key:
        os.environ["OPEN_ROUTER_KEY"] = args.openrouter_key
        print("OpenRouter API key set from command line argument")
    
    print(f"Starting CMB Agent MCP Server with base URL: {client.base_url}")
    
    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        print(f"Unsupported transport: {args.transport}")
