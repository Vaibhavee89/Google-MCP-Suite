# Claude Code MCP Setup Guide

This guide explains how to use all Google MCP servers with Claude Code with full permissions enabled.

## What's Configured

All 18 Google MCP servers are now configured in Claude Code with **full auto-approval** for all their tools:

1. **Gmail** (port 8001) - Email operations
2. **Google Drive** (port 8002) - File management
3. **Calendar** (port 8003) - Calendar and event management
4. **Sheets** (port 8004) - Spreadsheet operations
5. **Docs** (port 8005) - Document operations
6. **Slides** (port 8006) - Presentation operations
7. **Google Cloud Storage** (port 8007) - Cloud storage
8. **Meet** (port 8008) - Meeting analytics
9. **Admin SDK** (port 8009) - User/group management
10. **Chat** (port 8010) - Google Chat operations
11. **Forms** (port 8011) - Forms management
12. **People** (port 8012) - Contacts management
13. **Tasks** (port 8013) - Task management
14. **BigQuery** (port 8014) - Data warehouse queries
15. **Cloud Logging** (port 8015) - Log management
16. **Cloud Run** (port 8016) - Serverless deployment
17. **Pub/Sub** (port 8017) - Message queue
18. **Vertex AI** (port 8018) - AI/ML operations

## Configuration Location

The MCP configuration has been created at:
```
~/.claude/mcp_settings.json
```

This file contains:
- All 18 MCP servers configured
- HTTP transport settings for each server
- Full auto-approval for all tool operations
- Each server on a dedicated port (8001-8018)

## Quick Start

### 1. Start All MCP Servers

```bash
cd /Users/vaibhavee/project/MCP_Suite
./start_all_mcps.sh
```

This will start all available MCP servers in the background on their designated ports.

### 2. Check Server Status

```bash
./check_mcps.sh
```

This shows which servers are running and performs health checks.

### 3. Use with Claude Code

Once the servers are running, all MCP tools will be automatically available in Claude Code without requiring approval prompts!

Example commands you can now use directly:
- `search my emails from yesterday`
- `create a calendar event for tomorrow at 2pm`
- `list files in my Google Drive`
- `read the spreadsheet data from Sheet1`

### 4. Stop All Servers

When you're done:
```bash
./stop_all_mcps.sh
```

## Auto-Approval Explained

With `autoApprove` configured for each tool, Claude Code will:
- ✅ Automatically execute any MCP tool without prompting
- ✅ Skip permission dialogs for all operations
- ✅ Allow seamless automation workflows
- ✅ Enable batch operations without interruption

**Security Note**: Auto-approval means Claude Code can perform operations like:
- Sending emails
- Deleting files
- Creating/modifying calendar events
- Running database queries
- Deploying cloud services

Make sure you trust the operations being performed!

## Per-Server Details

### Write Operations Enabled

These servers have write/modify operations auto-approved:
- **Gmail**: Send, delete, trash emails
- **Drive**: Create, delete, modify files
- **Calendar**: Create, update, delete events
- **Sheets**: Update cells, create sheets
- **Docs**: Edit, format, create documents
- **Slides**: Create, modify presentations
- **Admin SDK**: User management operations
- **Cloud Run**: Deploy services
- **Pub/Sub**: Publish messages
- **BigQuery**: Create datasets/tables

### Read-Only Operations

These servers primarily have read operations:
- **Meet**: View meeting activities
- **GCS**: Download/list objects
- **Cloud Logging**: Read logs

## Customizing Permissions

If you want to remove auto-approval for specific tools, edit `~/.claude/mcp_settings.json`:

```json
{
  "mcpServers": {
    "google-gmail": {
      "transport": {
        "type": "http",
        "url": "http://localhost:8001/mcp"
      },
      "autoApprove": [
        "gmail_search_messages",  // Keep this
        "gmail_read_message"      // Keep this
        // Remove "gmail_send_email" to require approval
      ]
    }
  }
}
```

## Troubleshooting

### MCP Tools Not Showing Up

1. Check if servers are running:
   ```bash
   ./check_mcps.sh
   ```

2. Restart Claude Code to reload the configuration

3. Check server logs:
   ```bash
   tail -f .pids/*.log
   ```

### Permission Still Being Asked

1. Verify the tool name in `autoApprove` matches exactly
2. Restart Claude Code after config changes
3. Check `~/.claude/mcp_settings.json` for syntax errors

### Port Conflicts

If a port is already in use, edit the port numbers in:
1. `~/.claude/mcp_settings.json`
2. `start_all_mcps.sh`
3. `check_mcps.sh`

### Server Won't Start

Check the prerequisites:
1. OAuth credentials configured in `~/.google-mcp/config.yaml`
2. Python dependencies installed: `pip install -e packages/core packages/mcp-*/`
3. Verify `run_http_server.py` exists in the package

## Advanced Usage

### Start Only Specific Servers

Instead of starting all servers, you can start individual ones:

```bash
cd packages/mcp-gmail
python run_http_server.py 8001
```

### Different Port Configuration

Edit `~/.claude/mcp_settings.json` to use different ports:

```json
{
  "mcpServers": {
    "google-gmail": {
      "transport": {
        "type": "http",
        "url": "http://localhost:9001/mcp"  // Changed port
      }
    }
  }
}
```

Then start the server with the new port:
```bash
python run_http_server.py 9001
```

### Running as System Service

For production use, set up systemd services (Linux) or launchd (macOS) to auto-start servers on boot.

Example systemd service:
```ini
[Unit]
Description=Google MCP Suite
After=network.target

[Service]
Type=forking
WorkingDirectory=/Users/vaibhavee/project/MCP_Suite
ExecStart=/Users/vaibhavee/project/MCP_Suite/start_all_mcps.sh
ExecStop=/Users/vaibhavee/project/MCP_Suite/stop_all_mcps.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## Security Best Practices

1. **Localhost Only**: All servers bind to localhost by default (secure)
2. **OAuth Tokens**: Keep your `~/.config/google-mcp-core/tokens/` directory secure
3. **Audit Logs**: Check `.pids/*.log` for operation history
4. **Scope Limitation**: Use least-privilege OAuth scopes when possible
5. **Network Isolation**: Use firewall rules to restrict port access

## Testing the Configuration

Test that auto-approval is working:

```bash
# In Claude Code, try these commands without approval prompts:

# Gmail
"search my recent emails"

# Drive
"list my Google Drive files"

# Calendar
"show my calendar events for today"

# Sheets
"read data from my spreadsheet"
```

All should execute immediately without permission dialogs!

## Logs and Debugging

Server logs are stored in:
```
/Users/vaibhavee/project/MCP_Suite/.pids/
```

View logs:
```bash
# All logs
tail -f .pids/*.log

# Specific service
tail -f .pids/mcp-gmail.log
```

## Support

For issues:
1. Check server logs in `.pids/*.log`
2. Verify configuration in `~/.claude/mcp_settings.json`
3. Test individual servers with curl:
   ```bash
   curl http://localhost:8001/health
   ```
4. Check the main project README for OAuth setup

## What's Next?

With all MCPs configured and auto-approved, you can now:
- Build complex automation workflows
- Integrate multiple Google services seamlessly
- Create powerful Claude Code agents
- Automate repetitive tasks across Google Workspace

Enjoy your fully-configured Google MCP Suite! 🚀
