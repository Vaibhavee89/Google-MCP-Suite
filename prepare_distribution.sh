#!/bin/bash

# Google MCP Suite - Distribution Package Creator
# This script prepares a clean distribution package

set -e

echo "📦 Google MCP Suite - Distribution Package Creator"
echo "=================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create distribution directory
DIST_DIR="google-mcp-suite-distribution"
echo "🗂️  Creating distribution directory..."
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

# Copy project files
echo "📋 Copying project files..."

# Copy packages
cp -r packages "$DIST_DIR/"
echo "   ✓ Packages copied"

# Copy documentation
mkdir -p "$DIST_DIR/docs"
cp -r docs/* "$DIST_DIR/docs/" 2>/dev/null || true
cp 100_PERCENT_COMPLETE.md "$DIST_DIR/" 2>/dev/null || true
cp COMPLETE_IMPLEMENTATION_SUMMARY.md "$DIST_DIR/" 2>/dev/null || true
cp IMPLEMENTATION_STATUS.md "$DIST_DIR/" 2>/dev/null || true
echo "   ✓ Documentation copied"

# Copy setup scripts
cp SETUP.sh "$DIST_DIR/"
cp authenticate.py "$DIST_DIR/"
cp README_DISTRIBUTION.md "$DIST_DIR/README.md"
echo "   ✓ Setup scripts copied"

# Create .gitignore
echo "📝 Creating .gitignore..."
cat > "$DIST_DIR/.gitignore" << 'EOF'
# Virtual environment
.venv/
venv/
env/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Credentials (IMPORTANT!)
tokens.json
config.yaml
*.json
!package.json
!pyproject.toml

# Logs
*.log

# Testing
.pytest_cache/
.coverage
htmlcov/
EOF
echo "   ✓ .gitignore created"

# Clean up Python artifacts
echo "🧹 Cleaning Python artifacts..."
find "$DIST_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$DIST_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$DIST_DIR" -type f -name "*.pyo" -delete 2>/dev/null || true
find "$DIST_DIR" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
echo "   ✓ Cleaned"

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x "$DIST_DIR/SETUP.sh"
chmod +x "$DIST_DIR/authenticate.py"
echo "   ✓ Scripts are executable"

# Create SECURITY_NOTICE.txt
echo "🔒 Creating security notice..."
cat > "$DIST_DIR/SECURITY_NOTICE.txt" << 'EOF'
⚠️  IMPORTANT SECURITY NOTICE ⚠️

This package does NOT include OAuth credentials for security reasons.

You MUST:
1. Create your own Google Cloud Project
2. Enable required APIs
3. Create OAuth 2.0 credentials
4. Add credentials to ~/.google-mcp/config.yaml

DO NOT:
- Share your OAuth client_secret
- Commit credentials to version control
- Share your tokens.json file
- Use credentials from untrusted sources

See README.md for detailed setup instructions.
EOF
echo "   ✓ Security notice created"

# Create quick start guide
echo "📖 Creating quick start guide..."
cat > "$DIST_DIR/QUICKSTART.md" << 'EOF'
# Quick Start Guide

## 1. Run Setup (1 minute)
```bash
./SETUP.sh
```

## 2. Get OAuth Credentials (5 minutes)
1. Go to https://console.cloud.google.com/
2. Create project → Enable APIs → Create OAuth credentials
3. Download credentials

## 3. Configure (2 minutes)
```bash
nano ~/.google-mcp/config.yaml
```
Add your client_id and client_secret

## 4. Authenticate (1 minute)
```bash
./authenticate.sh
```
Grant permissions in browser

## 5. Test (30 seconds)
```bash
./test_server.sh drive
```

## 6. Use with Claude Code
```bash
claude mcp add google-drive -- $(pwd)/.venv/bin/python -m google_drive_mcp.server
```

Done! 🎉

See README.md for detailed instructions.
EOF
echo "   ✓ Quick start guide created"

# Create version info
echo "📌 Creating version info..."
cat > "$DIST_DIR/VERSION.txt" << EOF
Google MCP Suite
Version: 1.0.0
Build Date: $(date +"%Y-%m-%d %H:%M:%S")
Services: 9
Tools: 91
Python: 3.10+

Services Included:
- Google Drive (13 tools)
- Gmail (13 tools)
- Google Calendar (10 tools)
- Google Sheets (10 tools)
- Google Docs (9 tools)
- Google Slides (9 tools)
- Google Forms (10 tools)
- Google Tasks (10 tools)
- People API (9 tools)
EOF
echo "   ✓ Version info created"

# Create the zip file
echo ""
echo "🗜️  Creating zip archive..."
ZIP_NAME="google-mcp-suite-v1.0.0.zip"
rm -f "$ZIP_NAME"

# Use zip command
cd "$DIST_DIR"
zip -r "../$ZIP_NAME" . -x "*.pyc" -x "__pycache__/*" -x ".DS_Store" > /dev/null
cd ..

# Get zip size
ZIP_SIZE=$(du -h "$ZIP_NAME" | cut -f1)

echo "   ✓ Archive created: $ZIP_NAME ($ZIP_SIZE)"

# Clean up distribution directory
echo ""
echo "🧹 Cleaning up temporary files..."
rm -rf "$DIST_DIR"
echo "   ✓ Cleaned"

# Summary
echo ""
echo "=================================================="
echo -e "${GREEN}✅ Distribution Package Ready!${NC}"
echo "=================================================="
echo ""
echo "📦 Package: $ZIP_NAME"
echo "📊 Size: $ZIP_SIZE"
echo ""
echo "📋 What's included:"
echo "   ✓ All 9 MCP service packages"
echo "   ✓ Core utilities and authentication"
echo "   ✓ Setup and authentication scripts"
echo "   ✓ Complete documentation"
echo "   ✓ Quick start guide"
echo "   ✓ Security notices"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo "   This package does NOT include OAuth credentials"
echo "   Users must create their own Google Cloud project"
echo "   and configure OAuth credentials"
echo ""
echo "📤 To share:"
echo "   1. Upload $ZIP_NAME to your preferred platform"
echo "   2. Share the download link"
echo "   3. Users extract and run ./SETUP.sh"
echo ""
echo "🎉 Ready for distribution!"
echo ""
