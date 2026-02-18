#!/bin/bash

# Google MCP Suite - Automated Setup Script
# This script sets up the complete Google MCP Suite on your system

set -e  # Exit on error

echo "🚀 Google MCP Suite - Automated Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.10 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "   ✓ Python $PYTHON_VERSION found"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "   ✓ Virtual environment created"
else
    echo "   ✓ Virtual environment already exists"
fi

# Activate virtual environment
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

# Install core package
cd packages/core
pip install -e . > /dev/null 2>&1
cd ../..
echo "   ✓ Core package installed"

# Install all MCP packages
for package in packages/mcp-*/; do
    if [ -d "$package" ]; then
        package_name=$(basename "$package")
        cd "$package"
        pip install -e . > /dev/null 2>&1
        cd ../..
        echo "   ✓ $package_name installed"
    fi
done

# Create config directory
echo ""
echo "📁 Setting up configuration..."
CONFIG_DIR="$HOME/.google-mcp"
if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR"
    echo "   ✓ Config directory created at $CONFIG_DIR"
else
    echo "   ✓ Config directory exists at $CONFIG_DIR"
fi

# Copy config template if config doesn't exist
if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
    if [ -f "docs/config.example.yaml" ]; then
        cp docs/config.example.yaml "$CONFIG_DIR/config.yaml"
        echo "   ✓ Config template copied to $CONFIG_DIR/config.yaml"
        echo ""
        echo -e "${YELLOW}⚠️  IMPORTANT: You need to configure OAuth credentials!${NC}"
        echo "   Edit $CONFIG_DIR/config.yaml and add your:"
        echo "   - OAuth client_id"
        echo "   - OAuth client_secret"
        echo ""
    else
        echo -e "${RED}   ❌ Config template not found${NC}"
    fi
else
    echo "   ✓ Config file already exists"
fi

# Create authentication helper
echo ""
echo "🔐 Setting up authentication helper..."
cat > authenticate.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
python authenticate.py
EOF
chmod +x authenticate.sh
echo "   ✓ Authentication helper created"

# Create MCP server test script
echo ""
echo "🧪 Creating test script..."
cat > test_server.sh << 'EOF'
#!/bin/bash
# Test MCP Server Script
# Usage: ./test_server.sh <service-name>
# Example: ./test_server.sh drive

if [ -z "$1" ]; then
    echo "Usage: ./test_server.sh <service-name>"
    echo "Available services: drive, gmail, calendar, sheets, docs, slides, forms, tasks, people"
    exit 1
fi

SERVICE=$1
cd "$(dirname "$0")"
source .venv/bin/activate

case $SERVICE in
    drive)
        python -m google_drive_mcp.server
        ;;
    gmail)
        python -m google_gmail_mcp.server
        ;;
    calendar)
        python -m google_calendar_mcp.server
        ;;
    sheets)
        python -m google_sheets_mcp.server
        ;;
    docs)
        python -m google_docs_mcp.server
        ;;
    slides)
        python -m google_slides_mcp.server
        ;;
    forms)
        python -m google_forms_mcp.server
        ;;
    tasks)
        python -m google_tasks_mcp.server
        ;;
    people)
        python -m google_people_mcp.server
        ;;
    *)
        echo "Unknown service: $SERVICE"
        echo "Available services: drive, gmail, calendar, sheets, docs, slides, forms, tasks, people"
        exit 1
        ;;
esac
EOF
chmod +x test_server.sh
echo "   ✓ Test script created"

# Summary
echo ""
echo "======================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "======================================"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Configure OAuth Credentials:"
echo "   Edit: $CONFIG_DIR/config.yaml"
echo "   Add your Google OAuth client_id and client_secret"
echo ""
echo "2. Authenticate:"
echo "   Run: ./authenticate.sh"
echo "   This will open your browser for OAuth consent"
echo ""
echo "3. Test a service:"
echo "   Run: ./test_server.sh drive"
echo ""
echo "4. Add to Claude Code:"
echo "   Use 'claude mcp add' to register each service"
echo "   Example: claude mcp add google-drive -- $(pwd)/.venv/bin/python -m google_drive_mcp.server"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Complete guide"
echo "   - 100_PERCENT_COMPLETE.md - Feature list (91 tools!)"
echo "   - docs/claude-code-setup.md - Claude Code integration"
echo ""
echo "🎉 You now have access to 91 tools across 9 Google services!"
echo ""
