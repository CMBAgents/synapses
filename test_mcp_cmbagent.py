#!/usr/bin/env python3
"""
Test script for the CMB Agent MCP Server
This demonstrates how to use the MCP server programmatically
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_cmbagent_mcp():
    """Test the CMB Agent MCP server functionality."""
    
    # Server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_cmbagent.py", "stdio"],
        env={"PYTHONPATH": "."}
    )
    
    try:
        # Connect to the MCP server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("Connected to CMB Agent MCP Server!")
                
                # Test 1: List available programs
                print("\n=== Testing list_programs ===")
                try:
                    result = await session.call_tool("list_programs", {})
                    print(f"Available programs: {json.dumps(result.content, indent=2)}")
                except Exception as e:
                    print(f"Error listing programs: {e}")
                
                # Test 2: Check service health
                print("\n=== Testing check_service_health ===")
                try:
                    result = await session.call_tool("check_service_health", {})
                    print(f"Service health: {json.dumps(result.content, indent=2)}")
                except Exception as e:
                    print(f"Error checking health: {e}")
                
                # Test 3: Search for astronomy libraries
                print("\n=== Testing search_astronomy_libraries ===")
                try:
                    result = await session.call_tool("search_astronomy_libraries", {"query": "skyfield"})
                    print(f"Search results: {json.dumps(result.content, indent=2)}")
                except Exception as e:
                    print(f"Error searching libraries: {e}")
                
                # Test 4: Chat with astronomy chatbot
                print("\n=== Testing chat_with_astronomy ===")
                try:
                    result = await session.call_tool("chat_with_astronomy", {
                        "message": "What is python-skyfield and what can it do?",
                        "program_id": "skyfielders-python-skyfield"
                    })
                    print(f"Chat response: {json.dumps(result.content, indent=2)}")
                except Exception as e:
                    print(f"Error chatting: {e}")
                
                # Test 5: Get program context
                print("\n=== Testing get_program_context ===")
                try:
                    result = await session.call_tool("get_program_context", {
                        "program_id": "skyfielders-python-skyfield"
                    })
                    context = result.content
                    if isinstance(context, str) and len(context) > 100:
                        print(f"Context preview: {context[:100]}...")
                    else:
                        print(f"Context: {context}")
                except Exception as e:
                    print(f"Error getting context: {e}")
                
    except Exception as e:
        print(f"Failed to connect to MCP server: {e}")
        print("Make sure the MCP server is running and dependencies are installed")

if __name__ == "__main__":
    print("Testing CMB Agent MCP Server...")
    asyncio.run(test_cmbagent_mcp())
