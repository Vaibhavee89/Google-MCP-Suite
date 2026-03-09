# Quick Start Guide - Google Calendar MCP

Get up and running with the Google Calendar MCP server in 5 minutes!

## Step 1: Install Dependencies

```bash
cd packages/mcp-calendar
pip install -e .
```

## Step 2: Configure OAuth Credentials

You need Google Calendar API credentials. If you don't have them yet:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the Google Calendar API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download the credentials as `credentials.json`
6. Place it in your config directory (the server will guide you on first run)

## Step 3: Test STDIO Mode (Basic Test)

```bash
# This will run the MCP server in STDIO mode
python -m google_calendar_mcp.server
```

You should see the server start. Press `Ctrl+C` to stop.

## Step 4: Start HTTP Server

```bash
# Start the HTTP/SSE server for testing with MCP clients
python run_http_server.py 8000
```

You should see:
```
Starting Google Calendar MCP HTTP server on 0.0.0.0:8000
MCP endpoint: http://0.0.0.0:8000/mcp
Health check: http://0.0.0.0:8000/health
```

## Step 5: Verify Server is Running

Open a new terminal and run:

```bash
curl http://localhost:8000/health
```

Expected output: `ok`

## Step 6: Test with MCP Inspector

```bash
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

This will:
1. Open a web interface
2. Show available tools
3. Let you test each tool interactively

## Step 7: Configure Your MCP Client

### For Claude Desktop

Edit config file (macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "google-calendar": {
      "transport": {
        "type": "http",
        "url": "http://localhost:8000/mcp"
      }
    }
  }
}
```

Restart Claude Desktop.

### For Cline (VS Code)

Add to `.vscode/settings.json`:

```json
{
  "cline.mcpServers": {
    "google-calendar": {
      "transport": {
        "type": "http",
        "url": "http://localhost:8000/mcp"
      }
    }
  }
}
```

## Step 8: Try Your First Command

In your MCP client, try:

**List your calendars:**
```
Can you list my calendars?
```

**Check your schedule today:**
```
What's on my calendar today?
```

**Create an event:**
```
Create a meeting called "Team Sync" tomorrow at 2pm for 1 hour
```

**Check availability:**
```
Am I free tomorrow between 9am and 5pm?
```

## Available Commands (Tools)

Once connected, you can use these commands through your MCP client:

### Calendar Operations
- ✅ List all calendars
- ✅ Create a new calendar

### Event Operations
- ✅ Search/list events
- ✅ Get event details
- ✅ Create new events (with attendees, location, reminders)
- ✅ Update existing events
- ✅ Delete events
- ✅ Quick add events with natural language

### Attendee Management
- ✅ Add attendees to events
- ✅ Invite people automatically

### Availability
- ✅ Check free/busy status
- ✅ Find available time slots

### Advanced Features
- ✅ Set custom reminders (email, popup)
- ✅ Configure reminder timing
- ✅ Timezone support

## Example Commands

### Natural Language Event Creation

```
"Create a meeting called 'Project Review' next Monday at 3pm for 2 hours with john@example.com"
```

This automatically:
- Creates the event
- Sets the time
- Invites john@example.com
- Sends calendar invitation

### Check Availability for Multiple Calendars

```
"Check if I'm free tomorrow afternoon across all my calendars"
```

### Set Custom Reminders

```
"Create a doctor's appointment for next Friday at 10am with email reminder 1 day before and popup 30 minutes before"
```

## Troubleshooting

### Issue: Authentication error

**Solution:**
1. Make sure `credentials.json` is properly configured
2. Delete cached tokens: `rm -rf ~/.config/google-mcp-core/tokens/*`
3. Restart the server

### Issue: Connection refused

**Solution:**
1. Check if server is running: `curl http://localhost:8000/health`
2. Verify port 8000 is not in use: `lsof -i :8000`
3. Try a different port: `python run_http_server.py 3000`

### Issue: MCP client can't find the server

**Solution:**
1. Verify client config has correct URL
2. Restart MCP client after config change
3. Check server logs for errors
4. Test with MCP Inspector first

### Issue: OAuth consent screen errors

**Solution:**
1. Make sure Calendar API is enabled in Google Cloud Console
2. Add your email as a test user (if app is in testing mode)
3. Check OAuth scopes are correct

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [MCP_CLIENT_CONFIG.md](MCP_CLIENT_CONFIG.md) for advanced client configuration
- Explore all available tools through MCP Inspector
- Set up production deployment if needed

## Getting Help

- **Server not starting?** Check the error message and logs
- **Authentication issues?** Review Google Cloud Console setup
- **MCP client problems?** Test with MCP Inspector first
- **Other issues?** Open an issue in the repository

## Tips for Best Experience

1. **Keep server running** - Start it and leave it running in the background
2. **Use natural language** - The quick_add tool understands phrases like "tomorrow at 3pm"
3. **Check free/busy first** - Before scheduling, verify availability
4. **Set reminders** - Never miss an event with custom reminders
5. **Test with Inspector** - Validate tools work before using in production

## Security Reminders

⚠️ **Important:**
- Never commit `credentials.json` to git
- Keep OAuth tokens secure
- Use localhost binding for local development
- Implement proper authentication for production

---

**Estimated Setup Time:** 5-10 minutes

**Dependencies Installed:** ✅
**OAuth Configured:** ✅
**Server Running:** ✅
**MCP Client Connected:** ✅
**Ready to Use:** ✅

Enjoy your fully-featured Google Calendar MCP integration! 🎉
