#!/bin/bash
# Installation script for Google MCP Suite
# This script works around Python 3.13 editable install issues

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"

echo "=== Google MCP Suite Installation ==="
echo ""

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found at $VENV_DIR"
    echo "Please create it first with: python3 -m venv .venv"
    exit 1
fi

# Upgrade pip and setuptools
echo "Upgrading pip and setuptools..."
$PYTHON -m pip install --upgrade pip setuptools wheel

# Install all dependencies
echo ""
echo "Installing dependencies..."
$PIP install google-auth google-auth-oauthlib google-api-python-client PyYAML mcp requests \
    google-cloud-storage google-cloud-bigquery google-cloud-logging \
    google-cloud-pubsub google-cloud-run google-cloud-aiplatform

# Create .pth file to add packages to Python path
echo ""
echo "Setting up package paths..."
PTH_FILE="$VENV_DIR/lib/python3.13/site-packages/google_mcp_suite.pth"
cat > "$PTH_FILE" << EOF
$SCRIPT_DIR/packages/core/src
$SCRIPT_DIR/packages/mcp-google-drive/src
$SCRIPT_DIR/packages/mcp-gmail/src
$SCRIPT_DIR/packages/mcp-calendar/src
$SCRIPT_DIR/packages/mcp-sheets/src
$SCRIPT_DIR/packages/mcp-docs/src
$SCRIPT_DIR/packages/mcp-gcs/src
$SCRIPT_DIR/packages/mcp-meet/src
$SCRIPT_DIR/packages/mcp-admin-sdk/src
$SCRIPT_DIR/packages/mcp-chat/src
$SCRIPT_DIR/packages/mcp-slides/src
$SCRIPT_DIR/packages/mcp-forms/src
$SCRIPT_DIR/packages/mcp-tasks/src
$SCRIPT_DIR/packages/mcp-people/src
$SCRIPT_DIR/packages/mcp-bigquery/src
$SCRIPT_DIR/packages/mcp-cloudlogging/src
$SCRIPT_DIR/packages/mcp-pubsub/src
$SCRIPT_DIR/packages/mcp-cloudrun/src
$SCRIPT_DIR/packages/mcp-vertexai/src
EOF

echo "Package paths configured in: $PTH_FILE"

# Test imports
echo ""
echo "Testing imports..."
$PYTHON -c "
from google_mcp_core.config import load_config
from google_drive_mcp.service import DriveService
from google_gmail_mcp.service import GmailService
from google_calendar_mcp.service import CalendarService
from google_sheets_mcp.service import SheetsService
from google_docs_mcp.service import DocsService
from google_gcs_mcp.service import GCSService
from google_meet_mcp.service import MeetService
from google_admin_sdk_mcp.service import AdminSDKService
from google_chat_mcp.service import ChatService
from google_slides_mcp.service import SlidesService
from google_forms_mcp.service import FormsService
from google_tasks_mcp.service import TasksService
from google_people_mcp.service import PeopleService
from google_bigquery_mcp.service import BigQueryService
from google_cloudlogging_mcp.service import CloudLoggingService
from google_pubsub_mcp.service import PubSubService
from google_cloudrun_mcp.service import CloudRunService
from google_vertexai_mcp.service import VertexAIService
print('✓ All imports successful!')
"

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "1. Delete existing OAuth token: rm ~/.google-mcp/tokens.json"
echo "2. Re-authorize with all scopes (see docs/claude-code-setup.md)"
echo "3. Register MCPs with Claude Code using the commands in the setup guide"
echo ""
