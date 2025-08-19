#!/usr/bin/env python3
"""
Test script for the CMB Agent MCP Server - Main Branch Adapted
This demonstrates all MCP functionality using the unified chat API and main branch structure
"""

import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

def extract_content(result):
    """Extract text content from MCP tool result."""
    if hasattr(result, 'content') and result.content:
        # Handle TextContent objects
        if hasattr(result.content[0], 'text'):
            return result.content[0].text
        # Handle direct content
        return result.content
    return str(result)

async def test_all_functionality():
    """Test all functionality of the CMB Agent MCP server."""
    
    # Server parameters
    # NOTE: You need to get an OpenRouter API key from https://openrouter.ai/
    # Replace "your-openrouter-api-key-here" with your actual API key
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_cmbagent.py", "stdio", "--openrouter-key", "your-openrouter-api-key-here"],
        env={"PYTHONPATH": "."}
    )
    
    try:
        # Connect to the MCP server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("Connected to CMB Agent MCP Server (Main Branch Adapted)!")
                
                # Initialize the MCP session
                print("Initializing MCP session...")
                try:
                    init_result = await session.initialize()
                    print(f"Server initialized successfully!")
                except Exception as e:
                    print(f"Failed to initialize MCP session: {e}")
                    return
                
                print("Server is ready!")
                
                # Test 1: List Programs
                print("\n=== Testing List Programs ===")
                try:
                    result = await session.call_tool("list_programs", {})
                    programs = extract_content(result)
                    if isinstance(programs, list):
                        print(f"Found {len(programs)} programs")
                        for i, program in enumerate(programs[:5]):  # Show first 5
                            print(f"  {i+1}. {program.get('name', 'Unknown')} - {program.get('description', 'No description')[:60]}...")
                    else:
                        print(f"Programs response: {programs}")
                except Exception as e:
                    print(f"Error listing programs: {e}")
                
                # Test 2: Get Available Models
                print("\n=== Testing Get Available Models ===")
                try:
                    result = await session.call_tool("get_available_models", {})
                    models = extract_content(result)
                    if isinstance(models, list):
                        print(f"Found {len(models)} models")
                        for model in models:
                            print(f"  - {model.get('name', 'Unknown')} ({model.get('id', 'No ID')})")
                    else:
                        print(f"Models response: {models}")
                except Exception as e:
                    print(f"Error getting models: {e}")
                
                # Test 3: Get Program Context
                print("\n=== Testing Get Program Context ===")
                program_id = "skyfielders-python-skyfield"
                try:
                    result = await session.call_tool("get_program_context", {"program_id": program_id})
                    context = extract_content(result)
                    if context and not context.startswith("Error"):
                        print(f"Context for {program_id} retrieved successfully")
                        print(f"Context length: {len(context)} characters")
                        print(f"Preview: {context[:200]}...")
                    else:
                        print(f"Context error: {context}")
                except Exception as e:
                    print(f"Error getting context: {e}")
                
                # Test 4: Search Astronomy Libraries
                print("\n=== Testing Search Astronomy Libraries ===")
                search_query = "skyfield"
                try:
                    result = await session.call_tool("search_astronomy_libraries", {"query": search_query})
                    search_results = extract_content(result)
                    if isinstance(search_results, list):
                        print(f"Search for '{search_query}' returned {len(search_results)} results")
                        for result_item in search_results:
                            print(f"  - {result_item.get('name', 'Unknown')} ({result_item.get('id', 'No ID')})")
                    else:
                        print(f"Search response: {search_results}")
                except Exception as e:
                    print(f"Error searching libraries: {e}")
                
                # Test 5: Get Astronomy Leaderboard
                print("\n=== Testing Get Astronomy Leaderboard ===")
                try:
                    result = await session.call_tool("get_astronomy_leaderboard", {})
                    leaderboard = extract_content(result)
                    if isinstance(leaderboard, list):
                        print(f"Astronomy leaderboard has {len(leaderboard)} entries")
                        print("Top 5 libraries:")
                        for i, library in enumerate(leaderboard[:5]):
                            print(f"  {i+1}. {library.get('name', 'Unknown')} - {library.get('stars', 0)} stars")
                    else:
                        print(f"Leaderboard response: {leaderboard}")
                except Exception as e:
                    print(f"Error getting leaderboard: {e}")
                
                # Test 6: Get Finance Leaderboard
                print("\n=== Testing Get Finance Leaderboard ===")
                try:
                    result = await session.call_tool("get_finance_leaderboard", {})
                    leaderboard = extract_content(result)
                    if isinstance(leaderboard, list):
                        print(f"Finance leaderboard has {len(leaderboard)} entries")
                        for library in leaderboard:
                            print(f"  - {library.get('name', 'Unknown')} - {library.get('stars', 0)} stars")
                    else:
                        print(f"Finance leaderboard response: {leaderboard}")
                except Exception as e:
                    print(f"Error getting finance leaderboard: {e}")
                
                # Test 7: Get Program by ID
                print("\n=== Testing Get Program by ID ===")
                try:
                    result = await session.call_tool("get_program_by_id", {"program_id": program_id})
                    program_info = extract_content(result)
                    if isinstance(program_info, dict) and 'error' not in program_info:
                        print(f"Program info for {program_id}:")
                        print(f"  Name: {program_info.get('name', 'Unknown')}")
                        print(f"  Description: {program_info.get('description', 'No description')}")
                        print(f"  Stars: {program_info.get('stars', 'Unknown')}")
                        print(f"  Rank: {program_info.get('rank', 'Unknown')}")
                    else:
                        print(f"Program info response: {program_info}")
                except Exception as e:
                    print(f"Error getting program info: {e}")
                
                # Test 8: Check Service Health
                print("\n=== Testing Service Health ===")
                try:
                    result = await session.call_tool("check_service_health", {})
                    health = extract_content(result)
                    if isinstance(health, dict):
                        print(f"Service status: {health.get('status', 'Unknown')}")
                        print(f"Timestamp: {health.get('timestamp', 'Unknown')}")
                        if 'storage' in health:
                            print(f"Total contexts: {health['storage'].get('total_contexts', 'Unknown')}")
                    else:
                        print(f"Health response: {health}")
                except Exception as e:
                    print(f"Error checking health: {e}")
                
                # Test 9: Chat with Astronomy (if API key is available)
                print("\n=== Testing Chat with Astronomy ===")
                api_key = os.environ.get("OPEN_ROUTER_KEY")
                if api_key and api_key != "your-openrouter-api-key-here":
                    test_message = "What is python-skyfield and what can it do?"
                    try:
                        result = await session.call_tool("chat_with_astronomy", {
                            "message": test_message,
                            "program_id": program_id
                        })
                        
                        chat_response = extract_content(result)
                        if isinstance(chat_response, dict) and 'error' not in chat_response:
                            print(f"Chat response received successfully")
                            if 'choices' in chat_response and chat_response['choices']:
                                content = chat_response['choices'][0].get('message', {}).get('content', '')
                                print(f"Response preview: {content[:200]}...")
                        else:
                            print(f"Chat response: {chat_response}")
                    except Exception as e:
                        print(f"Error chatting: {e}")
                else:
                    print("Skipping chat test - OpenRouter API key not configured")
                    print("To test chat functionality, set OPEN_ROUTER_KEY environment variable")
                
                print("\n=== All Tests Completed ===")
                
    except Exception as e:
        print(f"Failed to connect to MCP server: {e}")
        print("Make sure the MCP server is running and dependencies are installed")

if __name__ == "__main__":
    print("Testing CMB Agent MCP Server - Main Branch Adapted")
    print("="*70)
    print("This test script will test all available MCP tools:")
    print("  - list_programs")
    print("  - get_available_models")
    print("  - get_program_context")
    print("  - search_astronomy_libraries")
    print("  - get_astronomy_leaderboard")
    print("  - get_finance_leaderboard")
    print("  - get_program_by_id")
    print("  - check_service_health")
    print("  - chat_with_astronomy (if API key available)")
    print("="*70)
    
    asyncio.run(test_all_functionality())
