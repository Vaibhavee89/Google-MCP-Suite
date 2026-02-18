# Setting Up Google MCP Suite with Claude Code

## Prerequisites
- Python 3.10+
- A Google Cloud project with APIs enabled
- OAuth 2.0 credentials (Desktop app type)

---

## Step 1: Create Google Cloud OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or use an existing one).
3. Go to **APIs & Services > Library** and enable the APIs you need:
   - Google Drive API
   - Gmail API
   - Google Calendar API
   - Google Sheets API
   - Google Docs API
   - (others as needed)
4. Go to **APIs & Services > Credentials**.
5. Click **Create Credentials > OAuth client ID**.
6. Choose **Desktop app** as the application type.
7. Download the JSON — you'll need the `client_id` and `client_secret`.

---

## Step 2: Create Config File

```bash
mkdir -p ~/.google-mcp
```

Create `~/.google-mcp/config.yaml`:

```yaml
google:
  auth_mode: oauth
  oauth:
    client_id: "YOUR_CLIENT_ID_HERE"
    client_secret: "YOUR_CLIENT_SECRET_HERE"
    redirect_uri: "http://localhost:8000/oauth/callback"
    token_store: "~/.google-mcp/tokens.json"
  service_account:
    keyfile: ""
    subject: ""
  default_scopes: []
services:
  drive:
    enabled: true
    scopes:
      - "https://www.googleapis.com/auth/drive.readonly"
  gmail:
    enabled: true
    scopes:
      - "https://www.googleapis.com/auth/gmail.readonly"
  calendar:
    enabled: true
    scopes:
      - "https://www.googleapis.com/auth/calendar.readonly"
  sheets:
    enabled: true
    scopes:
      - "https://www.googleapis.com/auth/spreadsheets.readonly"
  docs:
    enabled: true
    scopes:
      - "https://www.googleapis.com/auth/documents.readonly"
      - "https://www.googleapis.com/auth/drive.readonly"
```

---

## Step 3: Install Packages

```bash
cd /Users/vaibhavee/project/MCP_Suite

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install core + whichever services you want
pip install -e packages/core
pip install -e packages/mcp-google-drive
pip install -e packages/mcp-gmail
pip install -e packages/mcp-calendar
pip install -e packages/mcp-sheets
pip install -e packages/mcp-docs
pip install -e packages/mcp-gcs
pip install -e packages/mcp-meet
pip install -e packages/mcp-admin-sdk
pip install -e packages/mcp-chat
```

---

## Step 4: First-Time OAuth Login

The first time you use any MCP server, it will open a browser for Google OAuth consent.
You can trigger this manually to get it out of the way:

```bash
source /Users/vaibhavee/project/MCP_Suite/.venv/bin/activate
python -c "
from google_mcp_core.config import load_config
from google_mcp_core.auth.manager import AuthManager
config = load_config()
auth = AuthManager(config)
creds = auth.get_credentials('drive', ['https://www.googleapis.com/auth/drive.readonly'])
print('Auth successful!' if creds.valid else 'Token saved, refresh on next use.')
"
```

This saves a refresh token to `~/.google-mcp/tokens.json`. Subsequent calls reuse it.

---

## Step 5: Register MCP Servers in Claude Code

Run `claude mcp add` for each server you want. The command format is:

```bash
# Google Drive
claude mcp add google-drive -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_drive_mcp.server

# Gmail
claude mcp add google-gmail -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_gmail_mcp.server

# Calendar
claude mcp add google-calendar -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_calendar_mcp.server

# Sheets
claude mcp add google-sheets -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_sheets_mcp.server

# Docs
claude mcp add google-docs -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_docs_mcp.server

# GCS
claude mcp add google-gcs -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_gcs_mcp.server

# Meet
claude mcp add google-meet -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_meet_mcp.server

# Admin SDK
claude mcp add google-admin-sdk -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_admin_sdk_mcp.server

# Chat
claude mcp add google-chat -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_chat_mcp.server
```

### Alternative: Edit `.claude.json` directly

You can also add entries to `~/.claude.json` (or your project's `.mcp.json`):

```json
{
  "mcpServers": {
    "google-drive": {
      "command": "/Users/vaibhavee/project/MCP_Suite/.venv/bin/python",
      "args": ["-m", "google_drive_mcp.server"]
    },
    "google-gmail": {
      "command": "/Users/vaibhavee/project/MCP_Suite/.venv/bin/python",
      "args": ["-m", "google_gmail_mcp.server"]
    },
    "google-calendar": {
      "command": "/Users/vaibhavee/project/MCP_Suite/.venv/bin/python",
      "args": ["-m", "google_calendar_mcp.server"]
    },
    "google-sheets": {
      "command": "/Users/vaibhavee/project/MCP_Suite/.venv/bin/python",
      "args": ["-m", "google_sheets_mcp.server"]
    },
    "google-docs": {
      "command": "/Users/vaibhavee/project/MCP_Suite/.venv/bin/python",
      "args": ["-m", "google_docs_mcp.server"]
    },
    "google-gcs": {
      "command": "/Users/vaibhavee/project/MCP_Suite/.venv/bin/python",
      "args": ["-m", "google_gcs_mcp.server"]
    },
    "google-meet": {
      "command": "/Users/vaibhavee/project/MCP_Suite/.venv/bin/python",
      "args": ["-m", "google_meet_mcp.server"]
    },
    "google-admin-sdk": {
      "command": "/Users/vaibhavee/project/MCP_Suite/.venv/bin/python",
      "args": ["-m", "google_admin_sdk_mcp.server"]
    },
    "google-chat": {
      "command": "/Users/vaibhavee/project/MCP_Suite/.venv/bin/python",
      "args": ["-m", "google_chat_mcp.server"]
    }
  }
}
```

---

## Step 6: Test in Claude Code

Once registered, restart Claude Code. You should see the MCP tools available. Try:

- "Search my Drive for files containing 'report'"
- "Read my latest Gmail messages"
- "What events do I have this week?"
- "Read Sheet1!A1:D10 from spreadsheet ID xyz"

---

## Troubleshooting

| Issue | Fix |
| --- | --- |
| `ModuleNotFoundError` | Make sure you're using the venv python: `/Users/vaibhavee/project/MCP_Suite/.venv/bin/python` |
| OAuth browser doesn't open | Run the Step 4 auth script manually first |
| `FileNotFoundError: config` | Create `~/.google-mcp/config.yaml` per Step 2 |
| `google_http_403` | Enable the API in Google Cloud Console and check scopes |
| Token expired | Delete `~/.google-mcp/tokens.json` and re-auth |
