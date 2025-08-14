#!/bin/bash

# CMB Agent MCP Server Startup Script

echo "Starting CMB Agent MCP Server..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required packages are installed
# echo "Checking dependencies..."
# python3 -c "import mcp" 2>/dev/null || {
#     echo "Installing MCP dependencies..."
#     pip install -r requirements_mcp.txt
# }

# Set default values
BASE_URL=${BASE_URL:-"https://cmbchat.cloud"}
TRANSPORT=${TRANSPORT:-"stdio"}

echo "Configuration:"
echo "  Base URL: $BASE_URL"
echo "  Transport: $TRANSPORT"
echo ""

# Start the MCP server
echo "Starting server..."
python mcp_cmbagent.py $TRANSPORT --base-url "$BASE_URL"
