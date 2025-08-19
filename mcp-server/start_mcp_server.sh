#!/bin/bash

# CMB Agent MCP Server Startup Script - Main Branch Adapted
# This script starts the MCP server with intelligent configuration detection

echo "🚀 Starting CMB Agent MCP Server (Main Branch Adapted)..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking MCP dependencies..."
python3 -c "import mcp" 2>/dev/null || {
    echo "⚠️  MCP package not found. Installing dependencies..."
    pip install -r requirements_mcp.txt
}

# Check if FastMCP is available
python3 -c "import mcp.server.fastmcp" 2>/dev/null || {
    echo "⚠️  FastMCP package not found. Installing dependencies..."
    pip install -r requirements_mcp.txt
}

# Set default values
BASE_URL=${BASE_URL:-"http://localhost:3000"}
TRANSPORT=${TRANSPORT:-"stdio"}
OPEN_ROUTER_KEY=${OPEN_ROUTER_KEY:-""}

echo "🔧 Configuration:"
echo "  Base URL: $BASE_URL"
echo "  Transport: $TRANSPORT"
echo "  OpenRouter Key: ${OPEN_ROUTER_KEY:0:8}..."  # Show first 8 chars for security
echo ""

# Check if the MCP server file exists
if [ ! -f "mcp_cmbagent.py" ]; then
    echo "❌ Error: mcp_cmbagent.py not found in current directory"
    exit 1
fi

# Check if the config file exists
if [ ! -f "mcp_cmbagent_config.json" ]; then
    echo "⚠️  Warning: mcp_cmbagent_config.json not found"
fi

# Check if the test file exists
if [ ! -f "test_mcp_cmbagent.py" ]; then
    echo "⚠️  Warning: test_mcp_cmbagent.py not found"
fi

# Check if the requirements file exists
if [ ! -f "requirements_mcp.txt" ]; then
    echo "⚠️  Warning: requirements_mcp.txt not found"
fi

echo ""

# Check if OpenRouter key is set
if [ -z "$OPEN_ROUTER_KEY" ]; then
    echo "⚠️  Warning: OPEN_ROUTER_KEY environment variable is not set"
    echo "   Chat functionality may not work without an OpenRouter API key"
    echo "   Get your key from: https://openrouter.ai/"
    echo ""
fi

# Check if the base URL is accessible (optional check)
if [ "$BASE_URL" != "http://localhost:3000" ]; then
    echo "🔍 Checking if base URL is accessible..."
    if curl -s --head "$BASE_URL" > /dev/null; then
        echo "✅ Base URL is accessible"
    else
        echo "⚠️  Warning: Base URL may not be accessible"
    fi
    echo ""
fi

# Start the MCP server
echo "🚀 Starting server..."
if [ -n "$OPEN_ROUTER_KEY" ]; then
    python3 mcp_cmbagent.py $TRANSPORT --base-url "$BASE_URL" --openrouter-key "$OPEN_ROUTER_KEY"
else
    python3 mcp_cmbagent.py $TRANSPORT --base-url "$BASE_URL"
fi

echo ""
echo "✅ MCP server has stopped"
