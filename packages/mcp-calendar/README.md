# Google Calendar MCP Server

MCP server for Google Calendar with comprehensive calendar management features.

## Features

### ✅ Implemented Features

1. **OAuth 2.0 Authentication** - Secure authentication with Google Calendar API
2. **Calendar Management**
   - List all calendars
   - Create new calendars
3. **Event Management**
   - Search/list events with filters (time range, query)
   - Get event details by ID
   - Create events with attendees
   - Update existing events
   - Delete events
   - Quick add events using natural language
4. **Attendee Management**
   - Add attendees to events
   - Invite attendees automatically
5. **Availability Checking**
   - Check free/busy status across calendars
   - Find available time slots
6. **Reminders and Notifications**
   - Set custom reminders (email, popup)
   - Configure reminder timing

## Installation

```bash
# From the mcp-calendar directory
pip install -e .
```

## Configuration

The server uses the shared `google-mcp-core` configuration. Make sure you have:

1. OAuth credentials configured (via `google-mcp-core`)
2. Appropriate Calendar API scopes enabled

## Available Tools

### 1. calendar.search_events
Search for calendar events with optional filters.

**Parameters:**
- `calendar_id` (string, default: "primary") - Calendar to search in
- `query` (string, optional) - Free-text search query
- `time_min` (string, optional) - Start time filter (RFC3339)
- `time_max` (string, optional) - End time filter (RFC3339)
- `limit` (integer, default: 25) - Maximum results
- `page_token` (string, optional) - Pagination token

### 2. calendar.get_event
Get details of a specific event.

**Parameters:**
- `event_id` (string, required) - Event ID
- `calendar_id` (string, default: "primary") - Calendar ID

### 3. calendar.create_event
Create a new calendar event.

**Parameters:**
- `summary` (string, required) - Event title
- `start_time` (string, required) - Start time (RFC3339)
- `end_time` (string, required) - End time (RFC3339)
- `calendar_id` (string, default: "primary") - Calendar ID
- `description` (string, optional) - Event description
- `location` (string, optional) - Event location
- `attendees` (array of strings, optional) - Attendee email addresses
- `timezone` (string, default: "UTC") - Timezone
- `reminders` (object, optional) - Reminder settings

**Reminder Format:**
```json
{
  "useDefault": false,
  "overrides": [
    {"method": "email", "minutes": 30},
    {"method": "popup", "minutes": 10}
  ]
}
```

### 4. calendar.update_event
Update an existing event.

**Parameters:**
- `event_id` (string, required) - Event ID
- `calendar_id` (string, default: "primary") - Calendar ID
- `summary` (string, optional) - New title
- `start_time` (string, optional) - New start time
- `end_time` (string, optional) - New end time
- `description` (string, optional) - New description
- `location` (string, optional) - New location
- `timezone` (string, default: "UTC") - Timezone
- `reminders` (object, optional) - New reminder settings

### 5. calendar.delete_event
Delete a calendar event.

**Parameters:**
- `event_id` (string, required) - Event ID to delete
- `calendar_id` (string, default: "primary") - Calendar ID

### 6. calendar.list_calendars
List all accessible calendars.

**Parameters:** None

### 7. calendar.create_calendar
Create a new calendar.

**Parameters:**
- `summary` (string, required) - Calendar name
- `description` (string, optional) - Calendar description
- `timezone` (string, default: "UTC") - Calendar timezone

### 8. calendar.add_attendees
Add attendees to an existing event.

**Parameters:**
- `event_id` (string, required) - Event ID
- `attendees` (array of strings, required) - Email addresses to add
- `calendar_id` (string, default: "primary") - Calendar ID

### 9. calendar.quick_add_event
Create event using natural language (e.g., "Meeting tomorrow at 3pm").

**Parameters:**
- `text` (string, required) - Natural language event description
- `calendar_id` (string, default: "primary") - Calendar ID

### 10. calendar.check_freebusy
Check free/busy availability across calendars.

**Parameters:**
- `time_min` (string, required) - Start time to check (RFC3339)
- `time_max` (string, required) - End time to check (RFC3339)
- `calendar_ids` (array of strings, optional) - Calendar IDs (default: ["primary"])
- `timezone` (string, default: "UTC") - Timezone

## Running the Server

### Option 1: STDIO Mode (for MCP clients)

```bash
python -m google_calendar_mcp.server
```

### Option 2: HTTP/SSE Mode (for testing with HTTP clients)

```bash
# Run on default port 8000
python run_http_server.py

# Run on custom port
python run_http_server.py 3000

# Run on custom host and port
python run_http_server.py 3000 localhost
```

**Endpoints:**
- MCP endpoint: `http://localhost:8000/mcp`
- Health check: `http://localhost:8000/health`

### Testing with MCP Clients

You can test the HTTP server with any MCP-compatible client:

1. **Claude Desktop / Cline**: Configure to connect to `http://localhost:8000/mcp`
2. **MCP Inspector**: Use the HTTP transport option
3. **Custom clients**: Connect via HTTP/SSE to the `/mcp` endpoint

## Example Usage

### Create an event with reminders

```json
{
  "summary": "Team Meeting",
  "start_time": "2024-03-20T10:00:00Z",
  "end_time": "2024-03-20T11:00:00Z",
  "description": "Quarterly planning meeting",
  "location": "Conference Room A",
  "attendees": ["colleague@example.com"],
  "reminders": {
    "useDefault": false,
    "overrides": [
      {"method": "email", "minutes": 1440},
      {"method": "popup", "minutes": 30}
    ]
  }
}
```

### Check availability

```json
{
  "time_min": "2024-03-20T09:00:00Z",
  "time_max": "2024-03-20T17:00:00Z",
  "calendar_ids": ["primary", "team@example.com"]
}
```

### Quick add event

```json
{
  "text": "Lunch with John tomorrow at 1pm for 1 hour"
}
```

## Authentication

The server uses OAuth 2.0 authentication managed by `google-mcp-core`. On first run:

1. You'll be prompted to authenticate via browser
2. Credentials are cached for future use
3. Refresh tokens are automatically managed

## Required Scopes

- `https://www.googleapis.com/auth/calendar` - Full calendar access
- `https://www.googleapis.com/auth/calendar.readonly` - Read-only access
- `https://www.googleapis.com/auth/calendar.events` - Event management

## Development Timeline

✅ Completed in 1 day with AI assistance

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Ensure OAuth credentials are properly configured
2. **Connection Refused**: Check if the HTTP server is running on the correct port
3. **Missing Permissions**: Verify the required Calendar API scopes are enabled

### Debug Mode

Run with verbose logging:

```bash
python run_http_server.py 8000 --log-level debug
```

## Contributing

This is part of the Google MCP Suite. See the main repository for contribution guidelines.

## License

MIT License - See LICENSE file for details.
