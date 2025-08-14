#!/bin/bash

# Context Auto Updater Service Installation Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Installing Context Auto Updater Service${NC}"

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}Project directory: $PROJECT_DIR${NC}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}This script should not be run as root${NC}"
   exit 1
fi

# Check if systemd is available
if ! command -v systemctl &> /dev/null; then
    echo -e "${RED}systemd is not available on this system${NC}"
    exit 1
fi

# Create service file
SERVICE_FILE="/tmp/context-updater.service"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Context Auto Updater Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/python3 $PROJECT_DIR/scripts/auto-update-contexts.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=$PROJECT_DIR

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=context-updater

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$PROJECT_DIR/temp $PROJECT_DIR/app/context $PROJECT_DIR/public/context

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Service file created${NC}"

# Copy service file to systemd directory
sudo cp "$SERVICE_FILE" /etc/systemd/system/context-updater.service

echo -e "${GREEN}✅ Service file copied to systemd directory${NC}"

# Reload systemd
sudo systemctl daemon-reload

echo -e "${GREEN}✅ systemd daemon reloaded${NC}"

# Enable service
sudo systemctl enable context-updater.service

echo -e "${GREEN}✅ Service enabled${NC}"

# Start service
sudo systemctl start context-updater.service

echo -e "${GREEN}✅ Service started${NC}"

# Check service status
echo -e "${YELLOW}📊 Service status:${NC}"
sudo systemctl status context-updater.service --no-pager

echo -e "${GREEN}🎉 Installation complete!${NC}"
echo -e "${YELLOW}Useful commands:${NC}"
echo -e "  Check status: ${GREEN}sudo systemctl status context-updater${NC}"
echo -e "  View logs: ${GREEN}sudo journalctl -u context-updater -f${NC}"
echo -e "  Stop service: ${GREEN}sudo systemctl stop context-updater${NC}"
echo -e "  Restart service: ${GREEN}sudo systemctl restart context-updater${NC}"
echo -e "  Disable service: ${GREEN}sudo systemctl disable context-updater${NC}"

# Clean up
rm -f "$SERVICE_FILE" 