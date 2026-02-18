#!/bin/bash

# Google MCP Suite - Distribution with Credentials
# ⚠️  WARNING: This includes your OAuth credentials in the package
# Only use this if you understand the security implications

set -e

echo "⚠️  Google MCP Suite - Distribution with Credentials"
echo "====================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Security warning
echo -e "${RED}⚠️  SECURITY WARNING ⚠️${NC}"
echo ""
echo "This script will include your OAuth credentials in the package."
echo "This means:"
echo "  • Anyone with the package can access YOUR Google account"
echo "  • All API usage counts against YOUR quota"
echo "  • All actions appear as YOU in Google's logs"
echo "  • If the package is leaked, your account is compromised"
echo ""
echo -e "${YELLOW}Recommended: Use service account instead (safer)${NC}"
echo ""
read -p "Are you ABSOLUTELY sure you want to continue? (type 'YES' to proceed): " confirm

if [ "$confirm" != "YES" ]; then
    echo "Aborted. Good choice!"
    exit 0
fi

echo ""
echo "Proceeding with credential inclusion..."
echo ""

# Check if config exists
if [ ! -f "$HOME/.google-mcp/config.yaml" ]; then
    echo -e "${RED}❌ Config file not found at ~/.google-mcp/config.yaml${NC}"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create distribution directory
DIST_DIR="google-mcp-suite-with-credentials"
echo "🗂️  Creating distribution directory..."
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

# Copy project files
echo "📋 Copying project files..."
cp -r packages "$DIST_DIR/"
mkdir -p "$DIST_DIR/docs"
cp -r docs/* "$DIST_DIR/docs/" 2>/dev/null || true
cp 100_PERCENT_COMPLETE.md "$DIST_DIR/" 2>/dev/null || true
cp COMPLETE_IMPLEMENTATION_SUMMARY.md "$DIST_DIR/" 2>/dev/null || true
echo "   ✓ Project files copied"

# Copy credentials
echo "🔑 Copying credentials..."
mkdir -p "$DIST_DIR/credentials"
cp "$HOME/.google-mcp/config.yaml" "$DIST_DIR/credentials/"
if [ -f "$HOME/.google-mcp/tokens.json" ]; then
    cp "$HOME/.google-mcp/tokens.json" "$DIST_DIR/credentials/"
    echo "   ✓ OAuth tokens included"
fi
echo "   ✓ Credentials copied"

# Create easy setup script
echo "📝 Creating easy setup script..."
cat > "$DIST_DIR/EASY_SETUP.sh" << 'EOFSETUP'
#!/bin/bash

# Google MCP Suite - Easy Setup (Pre-configured)
# Credentials are included - just run this script!

set -e

echo "🚀 Google MCP Suite - Easy Setup"
echo "================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check Python
echo "📋 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    echo "   Download from: https://www.python.org/downloads/"
    exit 1
fi
echo "   ✓ Python found"

# Create virtual environment
echo ""
echo "🔧 Setting up virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "   ✓ Created"
else
    echo "   ✓ Already exists"
fi

source .venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing packages (this takes 2-3 minutes)..."
pip install --upgrade pip > /dev/null 2>&1

cd packages/core && pip install -e . > /dev/null 2>&1 && cd ../..
echo "   ✓ Core installed"

for pkg in packages/mcp-*/; do
    if [ -d "$pkg" ]; then
        name=$(basename "$pkg")
        cd "$pkg" && pip install -e . > /dev/null 2>&1 && cd ../..
        echo "   ✓ $name installed"
    fi
done

# Setup credentials
echo ""
echo "🔑 Setting up credentials..."
mkdir -p "$HOME/.google-mcp"
cp credentials/config.yaml "$HOME/.google-mcp/"
if [ -f "credentials/tokens.json" ]; then
    cp credentials/tokens.json "$HOME/.google-mcp/"
fi
echo "   ✓ Credentials configured"

# Create test script
cat > test_service.sh << 'EOF'
#!/bin/bash
if [ -z "$1" ]; then
    echo "Usage: ./test_service.sh <service>"
    echo "Services: drive, gmail, calendar, sheets, docs, slides, forms, tasks, people"
    exit 1
fi
cd "$(dirname "$0")"
source .venv/bin/activate
case $1 in
    drive) python -m google_drive_mcp.server ;;
    gmail) python -m google_gmail_mcp.server ;;
    calendar) python -m google_calendar_mcp.server ;;
    sheets) python -m google_sheets_mcp.server ;;
    docs) python -m google_docs_mcp.server ;;
    slides) python -m google_slides_mcp.server ;;
    forms) python -m google_forms_mcp.server ;;
    tasks) python -m google_tasks_mcp.server ;;
    people) python -m google_people_mcp.server ;;
    *) echo "Unknown: $1"; exit 1 ;;
esac
EOF
chmod +x test_service.sh

echo ""
echo "================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "================================="
echo ""
echo "🎉 Ready to use! No additional configuration needed."
echo ""
echo "📝 Quick Start:"
echo ""
echo "1. Test a service:"
echo "   ./test_service.sh drive"
echo ""
echo "2. Add to Claude Code:"
echo "   claude mcp add google-drive -- $(pwd)/.venv/bin/python -m google_drive_mcp.server"
echo ""
echo "   Repeat for: gmail, calendar, sheets, docs, slides, forms, tasks, people"
echo ""
echo "📚 See README.md for full documentation"
echo ""
echo -e "${YELLOW}⚠️  Note: This package uses shared credentials${NC}"
echo "   All users share the same Google account access"
echo ""
EOFSETUP

chmod +x "$DIST_DIR/EASY_SETUP.sh"
echo "   ✓ Setup script created"

# Create README
cat > "$DIST_DIR/README.md" << 'EOF'
# Google MCP Suite - Pre-Configured Package

## ⚠️ Important Notice

This package includes pre-configured OAuth credentials for easy setup.

**What this means:**
- ✅ No OAuth setup required
- ✅ Works immediately after setup
- ⚠️ All users share the same Google account access
- ⚠️ All API usage counts against the same quota
- ⚠️ All actions appear as the same user in logs

**Security Note:** Keep this package private. Do not share publicly.

## 🚀 Quick Setup (2 minutes)

### Step 1: Extract
```bash
unzip google-mcp-suite-with-credentials.zip
cd google-mcp-suite-with-credentials
```

### Step 2: Run Setup
```bash
chmod +x EASY_SETUP.sh
./EASY_SETUP.sh
```

That's it! The script will:
- Install all dependencies
- Configure credentials automatically
- Set up all 9 services

### Step 3: Test
```bash
./test_service.sh drive
```

### Step 4: Add to Claude Code
```bash
# Add each service you want to use
claude mcp add google-drive -- $(pwd)/.venv/bin/python -m google_drive_mcp.server
claude mcp add google-gmail -- $(pwd)/.venv/bin/python -m google_gmail_mcp.server
claude mcp add google-calendar -- $(pwd)/.venv/bin/python -m google_calendar_mcp.server
# ... etc for other services
```

## 📦 What's Included

- **9 Google Services**: Drive, Gmail, Calendar, Sheets, Docs, Slides, Forms, Tasks, People
- **91 Tools**: Full CRUD operations across all services
- **Pre-configured**: OAuth credentials included
- **Easy Setup**: One command installation

## 🎯 Available Services

1. **Google Drive** (13 tools) - File management, sharing, upload/download
2. **Gmail** (13 tools) - Send emails, manage labels, drafts
3. **Google Calendar** (10 tools) - Events, calendars, attendees
4. **Google Sheets** (10 tools) - Update cells, create spreadsheets
5. **Google Docs** (9 tools) - Create/edit documents
6. **Google Slides** (9 tools) - Create presentations
7. **Google Forms** (10 tools) - Create forms, add questions
8. **Google Tasks** (10 tools) - Manage tasks and lists
9. **People API** (9 tools) - Manage contacts

## 📋 Requirements

- Python 3.10 or higher
- Internet connection
- macOS, Linux, or Windows (with WSL)

## 🆘 Troubleshooting

### "Python not found"
Install Python from: https://www.python.org/downloads/

### "Permission denied"
Run: `chmod +x EASY_SETUP.sh`

### "Module not found"
Run the setup script again: `./EASY_SETUP.sh`

### API Quota Exceeded
All users share the same quota. Wait a few minutes and try again.

## 📚 Documentation

- `100_PERCENT_COMPLETE.md` - Complete feature list
- `docs/` - Additional documentation

## 🎉 Enjoy!

You now have access to 91 Google Workspace automation tools!
EOF

# Create .gitignore
cat > "$DIST_DIR/.gitignore" << 'EOF'
.venv/
__pycache__/
*.pyc
*.pyo
.DS_Store
*.log
EOF

# Clean up
echo ""
echo "🧹 Cleaning up..."
find "$DIST_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$DIST_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
echo "   ✓ Cleaned"

# Create zip
echo ""
echo "🗜️  Creating zip archive..."
ZIP_NAME="google-mcp-suite-with-credentials.zip"
rm -f "$ZIP_NAME"

cd "$DIST_DIR"
zip -r "../$ZIP_NAME" . -x "*.pyc" -x "__pycache__/*" > /dev/null
cd ..

ZIP_SIZE=$(du -h "$ZIP_NAME" | cut -f1)
echo "   ✓ Created: $ZIP_NAME ($ZIP_SIZE)"

# Cleanup
rm -rf "$DIST_DIR"

# Final warning
echo ""
echo "====================================================="
echo -e "${GREEN}✅ Package Created with Credentials${NC}"
echo "====================================================="
echo ""
echo "📦 File: $ZIP_NAME"
echo "📊 Size: $ZIP_SIZE"
echo ""
echo -e "${RED}⚠️  CRITICAL SECURITY REMINDERS:${NC}"
echo ""
echo "1. 🔒 Keep this package PRIVATE"
echo "2. 🚫 Do NOT upload to public repositories"
echo "3. 👥 Only share with trusted users"
echo "4. 📊 All users share YOUR API quota"
echo "5. 👤 All actions appear as YOU"
echo "6. 🔑 If leaked, revoke credentials immediately"
echo ""
echo "To revoke credentials if compromised:"
echo "  1. Go to: https://console.cloud.google.com/"
echo "  2. Navigate to: APIs & Services → Credentials"
echo "  3. Delete the OAuth client"
echo "  4. Create new credentials"
echo ""
echo "📤 Package ready for private distribution"
echo ""
