#!/bin/bash

# Google MCP Suite - Service Account Setup (Easier for Non-Technical Users)
# This version uses a service account key file for authentication

set -e

echo "🚀 Google MCP Suite - Easy Setup (Service Account)"
echo "===================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if service account key exists
if [ ! -f "service-account-key.json" ]; then
    echo -e "${RED}❌ Error: service-account-key.json not found${NC}"
    echo ""
    echo "This file should be included in the distribution package."
    echo "If you're the package creator, run: ./prepare_distribution_with_credentials.sh"
    exit 1
fi

echo "✓ Service account key found"
echo ""

# Check Python
echo "📋 Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.10 or higher from: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "   ✓ Python $PYTHON_VERSION found"

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "   ✓ Virtual environment created"
else
    echo "   ✓ Virtual environment already exists"
fi

source .venv/bin/activate

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "   ✓ pip upgraded"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
echo "   This may take a few minutes..."

cd packages/core
pip install -e . > /dev/null 2>&1
cd ../..
echo "   ✓ Core package installed"

for package in packages/mcp-*/; do
    if [ -d "$package" ]; then
        package_name=$(basename "$package")
        cd "$package"
        pip install -e . > /dev/null 2>&1
        cd ../..
        echo "   ✓ $package_name installed"
    fi
done

# Setup config directory
echo ""
echo "📁 Setting up configuration..."
CONFIG_DIR="$HOME/.google-mcp"
mkdir -p "$CONFIG_DIR"

# Copy service account key
cp service-account-key.json "$CONFIG_DIR/"
echo "   ✓ Service account key copied"

# Create config with service account
cat > "$CONFIG_DIR/config.yaml" << 'EOF'
auth_mode: service_account

service_account:
  keyfile: "~/.google-mcp/service-account-key.json"
  subject: ""  # Leave empty for service account

default_scopes:
  - "https://www.googleapis.com/auth/drive"

services:
  drive:
    enabled: true
    scopes:
      - "https://www.googleapis.com/auth/drive"
      - "https://www.googleapis.com/auth/drive.file"
      - "https://www.googleapis.com/auth/drive.readonly"
  
  gmail:
    enabled: true
    scopes:
      - "https://www.googleapis.com/auth/gmail.readonly"
      - "https://www.googleapis.com/auth/gmail.send"
      - "https://www.googleapis.com/auth/gmail.compose"
      - "https://www.googleapis.com/auth/gmail.modify"
  
  calendar:
    enabled: true
    scopes:
      - "https://www.googleapis.com/auth/calendar.readonly"
      - "https://www.googleapis.com/auth/calendar"
      - "https://www.googleapis.com/auth/calendar.events"
  
  sheets:
    enabled: true
    scopes:
      - "https://www.googleapis.com/auth/spreadsheets.readonly"
      - "https://www.googleapis.com/auth/spreadsheets"
  
  docs:
    enabled: true
    scopes:
      - "https://www.googleapis.com/auth/documents.readonly"
      - "https://www.googleapis.com/auth/documents"
  
  slides:
    enabled: true
    scopes:
      - "https://www.googleapis.com/auth/presentations.readonly"
      - "https://www.googleapis.com/auth/presentations"
      - "https://www.googleapis.com/auth/drive.file"
  
  forms:
    enabled: true
    scopes:
      - "https://www.googleapis.com/auth/forms.responses.readonly"
      - "https://www.googleapis.com/auth/forms.body.readonly"
      - "https://www.googleapis.com/auth/forms.body"
  
  tasks:
    enabled: true
    scopes:
      - "https://www.googleapis.com/auth/tasks.readonly"
      - "https://www.googleapis.com/auth/tasks"
  
  people:
    enabled: true
    scopes:
      - "https://www.googleapis.com/auth/contacts.readonly"
      - "https://www.googleapis.com/auth/contacts"
EOF

echo "   ✓ Configuration created"

# Create helper scripts
cat > test_server.sh << 'EOF'
#!/bin/bash
if [ -z "$1" ]; then
    echo "Usage: ./test_server.sh <service-name>"
    echo "Available: drive, gmail, calendar, sheets, docs, slides, forms, tasks, people"
    exit 1
fi

SERVICE=$1
cd "$(dirname "$0")"
source .venv/bin/activate

case $SERVICE in
    drive) python -m google_drive_mcp.server ;;
    gmail) python -m google_gmail_mcp.server ;;
    calendar) python -m google_calendar_mcp.server ;;
    sheets) python -m google_sheets_mcp.server ;;
    docs) python -m google_docs_mcp.server ;;
    slides) python -m google_slides_mcp.server ;;
    forms) python -m google_forms_mcp.server ;;
    tasks) python -m google_tasks_mcp.server ;;
    people) python -m google_people_mcp.server ;;
    *) echo "Unknown service: $SERVICE"; exit 1 ;;
esac
EOF
chmod +x test_server.sh

echo ""
echo "======================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "======================================"
echo ""
echo "🎉 Your Google MCP Suite is ready to use!"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Test a service:"
echo "   ./test_server.sh drive"
echo ""
echo "2. Add to Claude Code:"
echo "   claude mcp add google-drive -- $(pwd)/.venv/bin/python -m google_drive_mcp.server"
echo ""
echo "   Repeat for other services: gmail, calendar, sheets, docs, slides, forms, tasks, people"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Complete guide"
echo "   - 100_PERCENT_COMPLETE.md - All 91 tools"
echo ""
echo "⚠️  Note: Using service account authentication"
echo "   This is easier but has some limitations compared to OAuth"
echo ""
