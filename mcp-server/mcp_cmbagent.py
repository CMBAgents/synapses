import argparse
import requests
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("CMBAgentServer")

# Default configuration - adapté à la branche main
DEFAULT_BASE_URL = "http://localhost:3000"
DEFAULT_PROGRAM_ID = "skyfielders-python-skyfield"

class CMBAgentClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def get_programs(self) -> List[Dict[str, Any]]:
        """Get available programs from the config.json structure."""
        try:
            # Try to fetch from the config endpoint first
            response = self.session.get(f"{self.base_url}/api/context?domain=astronomy&action=getContextFiles")
            if response.status_code == 200:
                context_files = response.json()
                # Transform context files to program format
                programs = []
                for context_file in context_files:
                    if context_file.get('name') and context_file.get('content'):
                        # Extract program info from context file name
                        program_name = context_file['name']
                        # Try to find corresponding library info
                        library_info = self._find_library_info(program_name)
                        
                        programs.append({
                            "id": program_name,
                            "name": self._extract_display_name(program_name),
                            "description": library_info.get('description', f"Astronomy library: {program_name}"),
                            "stars": library_info.get('stars', 0),
                            "rank": library_info.get('rank', 0),
                            "github_url": library_info.get('github_url', ''),
                            "hasContextFile": True,
                            "contextFileName": f"{program_name}.txt"
                        })
                return programs
            else:
                # Fallback to hardcoded programs based on known structure
                return self._get_fallback_programs()
        except Exception as e:
            print(f"Error fetching programs: {e}")
            return self._get_fallback_programs()
    
    def _find_library_info(self, program_name: str) -> Dict[str, Any]:
        """Find library information from astronomy-libraries.json."""
        try:
            # Try to fetch from the data endpoint
            response = self.session.get(f"{self.base_url}/app/data/astronomy-libraries.json")
            if response.status_code == 200:
                libraries_data = response.json()
                for library in libraries_data.get('libraries', []):
                    if library.get('contextFileName', '').replace('-context.txt', '') == program_name:
                        return library
        except Exception:
            pass
        return {}
    
    def _extract_display_name(self, program_name: str) -> str:
        """Extract a readable display name from program name."""
        # Handle different naming patterns
        if '-' in program_name:
            # Convert "skyfielders-python-skyfield" to "python-skyfield"
            parts = program_name.split('-')
            if len(parts) >= 3 and parts[1] == 'python':
                return f"python-{parts[2]}"
            elif len(parts) >= 2:
                return parts[-1]  # Take the last part
        return program_name
    
    def _get_fallback_programs(self) -> List[Dict[str, Any]]:
        """Fallback programs when API is not available."""
        return [
            {
                "id": "skyfielders-python-skyfield",
                "name": "python-skyfield",
                "description": "skyfielders/python-skyfield - Astrophysics library with 1570 stars",
                "stars": 1570,
                "rank": 1,
                "github_url": "https://github.com/skyfielders/python-skyfield",
                "hasContextFile": True,
                "contextFileName": "skyfielders-python-skyfield-context.txt"
            },
            {
                "id": "dstndstn-astrometry-net",
                "name": "astrometry.net",
                "description": "dstndstn/astrometry.net - Astrophysics library with 750 stars",
                "stars": 750,
                "rank": 2,
                "github_url": "https://github.com/dstndstn/astrometry.net",
                "hasContextFile": True,
                "contextFileName": "dstndstn-astrometry-net-context.txt"
            },
            {
                "id": "astropy-astroquery",
                "name": "astroquery",
                "description": "astropy/astroquery - Astrophysics library with 739 stars",
                "stars": 739,
                "rank": 3,
                "github_url": "https://github.com/astropy/astroquery",
                "hasContextFile": True,
                "contextFileName": "astropy-astroquery-context.txt"
            },
            {
                "id": "einsteinpy-einsteinpy",
                "name": "einsteinpy",
                "description": "einsteinpy/einsteinpy - Astrophysics library with 650 stars",
                "stars": 650,
                "rank": 4,
                "github_url": "https://github.com/einsteinpy/einsteinpy",
                "hasContextFile": True,
                "contextFileName": "einsteinpy-einsteinpy-context.txt"
            },
            {
                "id": "lightkurve-lightkurve",
                "name": "lightkurve",
                "description": "lightkurve/lightkurve - Astrophysics library with 459 stars",
                "stars": 459,
                "rank": 5,
                "github_url": "https://github.com/lightkurve/lightkurve",
                "hasContextFile": True,
                "contextFileName": "lightkurve-lightkurve-context.txt"
            }
        ]
    
    def chat_with_program(self, program_id: str, message: str, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a chat message to a specific program using the unified chat API."""
        try:
            # Use the model_id if provided, otherwise use default from config
            if not model_id:
                model_id = "deepseek/deepseek-chat-v3-0324"
            
            payload = {
                "programId": program_id,
                "messages": [{"role": "user", "content": message}],
                "stream": False,  # Start with non-streaming for MCP compatibility
                "modelId": model_id,
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
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def get_context(self, program_id: str) -> str:
        """Get the context for a specific program using the context API."""
        try:
            # Try to get context from the context API
            response = self.session.get(
                f"{self.base_url}/api/context?domain=astronomy&action=loadContextFile&fileName={program_id}.txt"
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('content'):
                    return data['content']
            
            # Fallback: try to get from public context directory
            response = self.session.get(f"{self.base_url}/public/context/astronomy/{program_id}.txt")
            if response.status_code == 200:
                return response.text
            
            return f"Context not found for program: {program_id}"
        except Exception as e:
            return f"Error fetching context: {str(e)}"
    
    def get_health(self) -> Dict[str, Any]:
        """Check the health of the CMB Agent service using the health API."""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def get_leaderboard(self, domain: str = "astronomy") -> List[Dict[str, Any]]:
        """Get leaderboard data for a specific domain."""
        try:
            if domain == "astronomy":
                response = self.session.get(f"{self.base_url}/app/data/astronomy-libraries.json")
            elif domain == "finance":
                response = self.session.get(f"{self.base_url}/app/data/finance-libraries.json")
            else:
                return []
            
            if response.status_code == 200:
                data = response.json()
                return data.get('libraries', [])
            else:
                return []
        except Exception as e:
            print(f"Error fetching {domain} leaderboard: {e}")
            return []
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available models from the config."""
        try:
            # Try to get from config endpoint
            response = self.session.get(f"{self.base_url}/config.json")
            if response.status_code == 200:
                config = response.json()
                return config.get('availableModels', [])
            else:
                # Fallback to default models
                return [
                    {
                        "id": "deepseek/deepseek-chat-v3-0324",
                        "name": "DeepSeek Chat v3",
                        "description": "DeepSeek's latest chat model via OpenRouter"
                    },
                    {
                        "id": "openai/gpt-4",
                        "name": "GPT-4",
                        "description": "OpenAI's GPT-4 model"
                    },
                    {
                        "id": "anthropic/claude-3-opus",
                        "name": "Claude 3 Opus",
                        "description": "Anthropic's Claude 3 Opus model"
                    }
                ]
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []

# Initialize the client
client = CMBAgentClient()

@mcp.tool()
def list_programs() -> List[Dict[str, Any]]:
    """List all available programs in the CMB Agent system with detailed information."""
    programs = client.get_programs()
    return [{
        "id": p["id"], 
        "name": p["name"], 
        "description": p["description"],
        "stars": p.get("stars", 0),
        "rank": p.get("rank", 0),
        "github_url": p.get("github_url", ""),
        "hasContextFile": p.get("hasContextFile", False)
    } for p in programs]

@mcp.tool()
def chat_with_astronomy(message: str, program_id: str = DEFAULT_PROGRAM_ID, model_id: Optional[str] = None) -> Dict[str, Any]:
    """Chat with the astronomy chatbot using a specific program and optional model."""
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
def search_astronomy_libraries(query: str) -> List[Dict[str, Any]]:
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
                "description": program["description"],
                "stars": program.get("stars", 0),
                "rank": program.get("rank", 0),
                "github_url": program.get("github_url", "")
            })
    
    return results

@mcp.tool()
def get_astronomy_leaderboard() -> List[Dict[str, Any]]:
    """Get the astronomy leaderboard data."""
    return client.get_leaderboard("astronomy")

@mcp.tool()
def get_finance_leaderboard() -> List[Dict[str, Any]]:
    """Get the finance leaderboard data."""
    return client.get_leaderboard("finance")

@mcp.tool()
def get_available_models() -> List[Dict[str, Any]]:
    """Get available models that can be used with the chat system."""
    return client.get_available_models()

@mcp.tool()
def get_program_by_id(program_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific program by ID."""
    programs = client.get_programs()
    for program in programs:
        if program["id"] == program_id:
            return program
    return {"error": f"Program {program_id} not found"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CMB Agent MCP Server - Adapted for main branch")
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
    
    print(f"Starting CMB Agent MCP Server (main branch adapted) with base URL: {client.base_url}")
    print("Available tools:")
    print("  - list_programs")
    print("  - chat_with_astronomy")
    print("  - get_program_context")
    print("  - check_service_health")
    print("  - search_astronomy_libraries")
    print("  - get_astronomy_leaderboard")
    print("  - get_finance_leaderboard")
    print("  - get_available_models")
    print("  - get_program_by_id")
    
    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        print(f"Unsupported transport: {args.transport}")
