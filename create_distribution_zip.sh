#!/bin/bash

# Create Distribution Zip for Google MCP Suite
# This script packages the entire project for sharing

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Creating Google MCP Suite Distribution Package${NC}"
echo "================================================="
echo ""

# Get the base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="Google-MCP-Suite"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ZIP_NAME="${PROJECT_NAME}_${TIMESTAMP}.zip"

cd "$BASE_DIR"

echo -e "${BLUE}Cleaning up old build artifacts...${NC}"
# Remove old zip files
rm -f Google-MCP-Suite_*.zip 2>/dev/null || true

echo -e "${BLUE}Creating temporary staging directory...${NC}"
TEMP_DIR=$(mktemp -d)
STAGE_DIR="$TEMP_DIR/$PROJECT_NAME"
mkdir -p "$STAGE_DIR"

echo -e "${BLUE}Copying project files...${NC}"

# Copy main files
cp -r packages "$STAGE_DIR/"
cp -r docs "$STAGE_DIR/" 2>/dev/null || echo "No docs directory found"

# Copy configuration and documentation files
cp README.md "$STAGE_DIR/" 2>/dev/null || true
cp README_DISTRIBUTION.md "$STAGE_DIR/" 2>/dev/null || true
cp CLAUDE_CODE_SETUP.md "$STAGE_DIR/" 2>/dev/null || true
cp LICENSE "$STAGE_DIR/" 2>/dev/null || true
cp pyproject.toml "$STAGE_DIR/" 2>/dev/null || true
cp .gitignore "$STAGE_DIR/" 2>/dev/null || true

# Copy management scripts
cp start_all_mcps.sh "$STAGE_DIR/" 2>/dev/null || true
cp stop_all_mcps.sh "$STAGE_DIR/" 2>/dev/null || true
cp check_mcps.sh "$STAGE_DIR/" 2>/dev/null || true

# Copy setup scripts if they exist
cp SETUP.sh "$STAGE_DIR/" 2>/dev/null || true
cp authenticate.sh "$STAGE_DIR/" 2>/dev/null || true
cp test_server.sh "$STAGE_DIR/" 2>/dev/null || true

# Create a sample Claude Code config
mkdir -p "$STAGE_DIR/examples"
cp ~/.claude/mcp_settings.json "$STAGE_DIR/examples/claude_code_mcp_settings.json" 2>/dev/null || true

echo -e "${BLUE}Cleaning up Python artifacts...${NC}"
# Remove Python cache and build artifacts
find "$STAGE_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$STAGE_DIR" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find "$STAGE_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$STAGE_DIR" -type f -name "*.pyo" -delete 2>/dev/null || true
find "$STAGE_DIR" -type f -name ".DS_Store" -delete 2>/dev/null || true

# Remove virtual environment if it was copied
rm -rf "$STAGE_DIR/.venv" 2>/dev/null || true
rm -rf "$STAGE_DIR/venv" 2>/dev/null || true

# Remove git directory
rm -rf "$STAGE_DIR/.git" 2>/dev/null || true

# Remove any local config or tokens
rm -rf "$STAGE_DIR/.google-mcp" 2>/dev/null || true
rm -f "$STAGE_DIR/tokens.json" 2>/dev/null || true
rm -f "$STAGE_DIR/credentials.json" 2>/dev/null || true

# Remove .pids directory
rm -rf "$STAGE_DIR/.pids" 2>/dev/null || true

echo -e "${BLUE}Creating README for distribution...${NC}"

# Create a distribution README
cat > "$STAGE_DIR/START_HERE.md" << 'EOF'
# 🚀 Google MCP Suite - Quick Start Guide

Welcome to the **Google MCP Suite**! This package provides comprehensive integration with Google services for Claude Code.

## 📦 What's Inside

**18 Google Service Integrations** with full automation capabilities:
- Gmail, Drive, Calendar, Sheets, Docs, Slides
- Cloud Storage (GCS), BigQuery, Cloud Run
- Pub/Sub, Cloud Logging, Vertex AI
- Meet, Chat, Forms, Tasks, People API, Admin SDK

**200+ Tools** for comprehensive Google Workspace automation!

## 🎯 Quick Setup (5 Minutes)

### Step 1: Extract & Navigate
```bash
cd Google-MCP-Suite
```

### Step 2: Configure OAuth (One Time)

1. **Get Google OAuth Credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project and enable APIs (Drive, Gmail, Calendar, etc.)
   - Create OAuth 2.0 credentials (Desktop app type)
   - Download the credentials

2. **Create Config Directory**:
   ```bash
   mkdir -p ~/.google-mcp
   ```

3. **Create Config File**:
   ```bash
   nano ~/.google-mcp/config.yaml
   ```

4. **Add Your OAuth Credentials**:
   ```yaml
   auth_mode: oauth
   oauth:
     client_id: "YOUR_CLIENT_ID.apps.googleusercontent.com"
     client_secret: "YOUR_CLIENT_SECRET"
     redirect_uri: "http://localhost:3080/gdrive/oauth/callback"
   ```

### Step 3: Install Dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all packages
pip install -e packages/core
pip install -e packages/mcp-gmail
pip install -e packages/mcp-google-drive
pip install -e packages/mcp-calendar
pip install -e packages/mcp-sheets
pip install -e packages/mcp-docs
pip install -e packages/mcp-slides
pip install -e packages/mcp-gcs
pip install -e packages/mcp-meet
pip install -e packages/mcp-admin-sdk
pip install -e packages/mcp-chat
pip install -e packages/mcp-forms
pip install -e packages/mcp-people
pip install -e packages/mcp-tasks
pip install -e packages/mcp-bigquery
pip install -e packages/mcp-cloudlogging
pip install -e packages/mcp-cloudrun
pip install -e packages/mcp-pubsub
pip install -e packages/mcp-vertexai
```

### Step 4: Set Up Claude Code (IMPORTANT!)

**Option A: Use Pre-Configured Settings (Recommended)**

```bash
# Copy the pre-configured Claude Code settings
mkdir -p ~/.claude
cp examples/claude_code_mcp_settings.json ~/.claude/mcp_settings.json
```

**Option B: Manual Configuration**

See `CLAUDE_CODE_SETUP.md` for detailed manual setup instructions.

### Step 5: Start the Servers

```bash
# Make scripts executable
chmod +x *.sh

# Start all MCP servers
./start_all_mcps.sh

# Verify they're running
./check_mcps.sh
```

### Step 6: Authenticate (First Time Only)

The first time you use a service, you'll be prompted to authenticate via your browser. This is normal!

```bash
# Test authentication by starting one server
cd packages/mcp-gmail
python run_http_server.py 8001
```

A browser window will open. Sign in and grant permissions.

### Step 7: Use with Claude Code! 🎉

Restart Claude Code, and all Google services will be available with **full auto-approval** (no permission prompts)!

Try commands like:
- "Search my emails from yesterday"
- "List files in my Google Drive"
- "Create a calendar event for tomorrow at 2pm"
- "Read data from my spreadsheet"

## 📚 Important Documentation

- **CLAUDE_CODE_SETUP.md** - Complete Claude Code integration guide
- **README_DISTRIBUTION.md** - Full feature list and capabilities
- **README.md** - Project overview and architecture

## 🔥 Key Features

✅ **Full Auto-Approval** - All 200+ tools work without permission prompts
✅ **18 Services** - Comprehensive Google Workspace coverage
✅ **Easy Management** - Start/stop scripts included
✅ **Production Ready** - HTTP servers with health checks
✅ **Secure** - OAuth 2.0, localhost-only by default

## 🛠️ Management Commands

```bash
# Start all servers
./start_all_mcps.sh

# Check server status
./check_mcps.sh

# Stop all servers
./stop_all_mcps.sh
```

## ⚠️ Important Notes

1. **OAuth Required**: You MUST configure OAuth credentials before use
2. **Enable APIs**: Enable all required APIs in Google Cloud Console
3. **Auto-Approval**: All operations execute without prompts (powerful but use carefully!)
4. **Security**: Keep your OAuth credentials and tokens private
5. **Localhost Only**: Servers bind to localhost by default (secure)

## 🐛 Troubleshooting

### "No module named 'google_mcp_core'"
```bash
# Make sure you're in the virtual environment
source .venv/bin/activate
pip install -e packages/core
```

### "Authentication failed"
```bash
# Check your config file
cat ~/.google-mcp/config.yaml

# Delete tokens and re-authenticate
rm -rf ~/.config/google-mcp-core/tokens/
# Restart a server to trigger re-auth
```

### "Port already in use"
```bash
# Stop all servers first
./stop_all_mcps.sh
# Then restart
./start_all_mcps.sh
```

### "MCP tools not showing in Claude Code"
1. Verify servers are running: `./check_mcps.sh`
2. Check config: `cat ~/.claude/mcp_settings.json`
3. Restart Claude Code
4. Check server logs: `tail -f .pids/*.log`

## 📖 Next Steps

1. ✅ Complete OAuth setup
2. ✅ Install dependencies
3. ✅ Copy Claude Code config
4. ✅ Start servers
5. ✅ Authenticate
6. ✅ Start using with Claude Code!

## 🎉 You're All Set!

Read **CLAUDE_CODE_SETUP.md** for advanced configuration, security best practices, and troubleshooting.

**Happy Automating!** 🚀
EOF

echo -e "${BLUE}Creating zip archive...${NC}"
cd "$TEMP_DIR"
zip -r "$BASE_DIR/$ZIP_NAME" "$PROJECT_NAME" -q

echo -e "${BLUE}Cleaning up...${NC}"
rm -rf "$TEMP_DIR"

# Calculate size
SIZE=$(du -h "$BASE_DIR/$ZIP_NAME" | cut -f1)

echo ""
echo -e "${GREEN}✓ Distribution package created successfully!${NC}"
echo ""
echo -e "${YELLOW}Package Details:${NC}"
echo "  File: $ZIP_NAME"
echo "  Size: $SIZE"
echo "  Location: $BASE_DIR/$ZIP_NAME"
echo ""
echo -e "${GREEN}📦 Ready to share!${NC}"
echo ""
echo -e "${BLUE}Package Contents:${NC}"
echo "  ✓ All 18 MCP packages"
echo "  ✓ Core framework"
echo "  ✓ Management scripts (start/stop/check)"
echo "  ✓ Claude Code configuration example"
echo "  ✓ Complete documentation"
echo "  ✓ Setup instructions"
echo ""
echo -e "${YELLOW}Recipients should:${NC}"
echo "  1. Extract the zip file"
echo "  2. Read START_HERE.md"
echo "  3. Follow the Quick Setup guide"
echo "  4. Configure OAuth credentials"
echo "  5. Install dependencies and start servers"
echo ""
echo -e "${GREEN}Done! 🎉${NC}"
