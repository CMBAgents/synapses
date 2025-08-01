#!/bin/bash

# CMBAgent Config Updater Installation Script
# This script installs and configures the automatic config.json updater service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="cmbagent-config-updater"
SERVICE_FILE="config-updater.service"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SERVICE_USER="cmbagent"
SERVICE_GROUP="cmbagent"

echo -e "${BLUE}🚀 CMBAgent Config Updater Installation${NC}"
echo "=================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ This script should not be run as root${NC}"
   exit 1
fi

# Check if project directory exists
if [[ ! -d "$PROJECT_DIR" ]]; then
    echo -e "${RED}❌ Project directory not found: $PROJECT_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Project directory: $PROJECT_DIR${NC}"

# Check if required files exist
required_files=(
    "scripts/update-config-from-contexts.py"
    "scripts/config-updater.service"
    "app/data/astronomy-libraries.json"
    "app/data/finance-libraries.json"
)

for file in "${required_files[@]}"; do
    if [[ ! -f "$PROJECT_DIR/$file" ]]; then
        echo -e "${RED}❌ Required file not found: $file${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Found: $file${NC}"
done

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 is available${NC}"

# Test the config updater script
echo -e "${YELLOW}🧪 Testing config updater script...${NC}"
cd "$PROJECT_DIR"

if python3 scripts/update-config-from-contexts.py --help &> /dev/null; then
    echo -e "${GREEN}✅ Config updater script test passed${NC}"
else
    echo -e "${RED}❌ Config updater script test failed${NC}"
    exit 1
fi

# Create service user if it doesn't exist
if ! id "$SERVICE_USER" &>/dev/null; then
    echo -e "${YELLOW}👤 Creating service user: $SERVICE_USER${NC}"
    sudo useradd -r -s /bin/false -d "$PROJECT_DIR" "$SERVICE_USER"
    echo -e "${GREEN}✅ Service user created${NC}"
else
    echo -e "${GREEN}✅ Service user already exists: $SERVICE_USER${NC}"
fi

# Set proper permissions
echo -e "${YELLOW}🔐 Setting permissions...${NC}"
sudo chown -R "$SERVICE_USER:$SERVICE_GROUP" "$PROJECT_DIR"
sudo chmod -R 755 "$PROJECT_DIR"
sudo chmod +x "$PROJECT_DIR/scripts/update-config-from-contexts.py"

echo -e "${GREEN}✅ Permissions set${NC}"

# Copy service file to systemd directory
echo -e "${YELLOW}📋 Installing systemd service...${NC}"
sudo cp "$PROJECT_DIR/scripts/$SERVICE_FILE" "/etc/systemd/system/$SERVICE_NAME.service"

# Update service file with correct paths
sudo sed -i "s|/opt/cmbagent-info|$PROJECT_DIR|g" "/etc/systemd/system/$SERVICE_NAME.service"
sudo sed -i "s|cmbagent|$SERVICE_USER|g" "/etc/systemd/system/$SERVICE_NAME.service"

echo -e "${GREEN}✅ Service file installed${NC}"

# Reload systemd and enable service
echo -e "${YELLOW}🔄 Reloading systemd...${NC}"
sudo systemctl daemon-reload

echo -e "${YELLOW}🔧 Enabling service...${NC}"
sudo systemctl enable "$SERVICE_NAME"

echo -e "${GREEN}✅ Service enabled${NC}"

# Create log directory
sudo mkdir -p /var/log/cmbagent
sudo chown "$SERVICE_USER:$SERVICE_GROUP" /var/log/cmbagent

echo -e "${GREEN}✅ Log directory created${NC}"

# Display installation summary
echo ""
echo -e "${BLUE}📋 Installation Summary${NC}"
echo "========================"
echo -e "Service Name: ${GREEN}$SERVICE_NAME${NC}"
echo -e "Service User: ${GREEN}$SERVICE_USER${NC}"
echo -e "Project Directory: ${GREEN}$PROJECT_DIR${NC}"
echo -e "Check Interval: ${GREEN}10 minutes${NC}"
echo -e "Log File: ${GREEN}/var/log/cmbagent/config_update.log${NC}"

echo ""
echo -e "${YELLOW}⚠️  Next Steps:${NC}"
echo "1. Edit /etc/systemd/system/$SERVICE_NAME.service"
echo "2. Set your GITHUB_TOKEN in the Environment section"
echo "3. Start the service: sudo systemctl start $SERVICE_NAME"
echo "4. Check status: sudo systemctl status $SERVICE_NAME"
echo "5. View logs: sudo journalctl -u $SERVICE_NAME -f"

echo ""
echo -e "${GREEN}🎉 Installation completed successfully!${NC}" 