import argparse
import requests
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("CMBAgentServer")

# Default configuration
DEFAULT_BASE_URL = "https://cmbchat.cloud"
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
                        "description": "skyfielders/python-skyfield - Astrophysics library with 1570 stars"
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
    
    def chat_with_program(self, program_id: str, message: str, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a chat message to a specific program."""
        try:
            payload = {
                "programId": program_id,
                "messages": [{"role": "user", "content": message}],
                "stream": False
            }
            
            if model_id:
                payload["modelId"] = model_id
            
            response = self.session.post(
                f"{self.base_url}/api/unified-chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
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
def chat_with_astronomy(message: str, program_id: str = DEFAULT_PROGRAM_ID, model_id: Optional[str] = None) -> Dict[str, Any]:
    """Chat with the astronomy chatbot using a specific program."""
    return client.chat_with_program(program_id, message, model_id)

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

@mcp.tool()
def get_astronomy_leaderboard() -> Dict[str, Any]:
    """Get the astronomy leaderboard data."""
    try:
        response = client.session.get(f"{client.base_url}/astronomy/leaderboard")
        if response.status_code == 200:
            return {"status": "success", "data": "Leaderboard data retrieved"}
        else:
            return {"status": "error", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
def get_finance_leaderboard() -> Dict[str, Any]:
    """Get the finance leaderboard data."""
    try:
        response = client.session.get(f"{client.base_url}/finance/leaderboard")
        if response.status_code == 200:
            return {"status": "success", "data": "Finance leaderboard data retrieved"}
        else:
            return {"status": "error", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CMB Agent MCP Server")
    parser.add_argument("transport", choices=["stdio", "sse"], help="Transport mode")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL for CMB Agent service")
    args = parser.parse_args()
    
    # Update client with custom base URL if provided
    if args.base_url != DEFAULT_BASE_URL:
        client = CMBAgentClient(args.base_url)
    
    print(f"Starting CMB Agent MCP Server with base URL: {client.base_url}")
    mcp.run(transport=args.transport)
