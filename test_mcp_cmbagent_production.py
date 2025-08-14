#!/usr/bin/env python3
"""
Test script for the CMB Agent MCP Server - Production Server
This demonstrates the chat functionality using the production server at cmbchat.cloud
"""

import asyncio
import json
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

async def test_production_chat():
    """Test the chat functionality against the production server."""
    
    # Server parameters - using production server
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_cmbagent_production.py", "stdio", "--openrouter-key", "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"],
        env={"PYTHONPATH": "."}
    )
    
    try:
        # Connect to the MCP server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("Connected to CMB Agent MCP Server (Production)!")
                print("Server: cmbchat.cloud")
                
                # Initialize the MCP session
                print("Initializing MCP session...")
                try:
                    init_result = await session.initialize()
                    print(f"Server initialized successfully!")
                except Exception as e:
                    print(f"Failed to initialize MCP session: {e}")
                    return
                
                print("Server is ready!")
                
                # Test chat functionality
                print("\n=== Testing Chat with Astronomy (Production) ===")
                print("Using default model: deepseek/deepseek-chat-v3-0324 (via OpenRouter)")
                
                test_message = "What is python-skyfield and what can it do?"
                program_id = "skyfielders-python-skyfield"
                
                print(f"\nSending message: {test_message}")
                print(f"Program: {program_id}")
                
                try:
                    result = await session.call_tool("chat_with_astronomy", {
                        "message": test_message,
                        "program_id": program_id
                    })
                    
                    content = extract_content(result)
                    print(f"\nChat Response:")
                    print(f"{'='*50}")
                    print(content)
                    print(f"{'='*50}")
                    
                except Exception as e:
                    print(f"Error chatting: {e}")
                
    except Exception as e:
        print(f"Failed to connect to MCP server: {e}")
        print("Make sure the MCP server is running and dependencies are installed")

if __name__ == "__main__":
    print("Testing CMB Agent MCP Server - Production Server")
    print("Server: cmbchat.cloud")
    print("Default Model: deepseek/deepseek-chat-v3-0324 (via OpenRouter)")
    print("="*70)
    asyncio.run(test_production_chat())
