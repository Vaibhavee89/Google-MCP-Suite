from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_calendar_mcp.service import CalendarService

app = Server("google-calendar-mcp")


@lru_cache(maxsize=1)
def _svc() -> CalendarService:
    """One service per process: config is read once and Google clients are reused."""
    return CalendarService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="calendar_search_events",
            description="Search Calendar events with optional query/time filters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "calendar_id": {"type": "string", "description": "Calendar ID.", "default": "primary"},
                    "query": {"type": "string", "description": "Free-text search query."},
                    "time_min": {"type": "string", "description": "Lower bound (RFC3339) for event start."},
                    "time_max": {"type": "string", "description": "Upper bound (RFC3339) for event start."},
                    "limit": {"type": "integer", "description": "Max results.", "default": 25},
                    "page_token": {"type": "string", "description": "Pagination token."},
                },
            },
        ),
        Tool(
            name="calendar_get_event",
            description="Get a Calendar event by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "Calendar event ID."},
                    "calendar_id": {"type": "string", "description": "Calendar ID.", "default": "primary"},
                },
                "required": ["event_id"],
            },
        ),
        Tool(
            name="calendar_create_event",
            description="Create a new calendar event.",
            inputSchema={
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Event title."},
                    "start_time": {"type": "string", "description": "Start time (RFC3339)."},
                    "end_time": {"type": "string", "description": "End time (RFC3339)."},
                    "calendar_id": {"type": "string", "description": "Calendar ID.", "default": "primary"},
                    "description": {"type": "string", "description": "Event description."},
                    "location": {"type": "string", "description": "Event location."},
                    "attendees": {"type": "array", "items": {"type": "string"}, "description": "Attendee emails."},
                    "timezone": {"type": "string", "description": "Timezone.", "default": "UTC"},
                    "reminders": {
                        "type": "object",
                        "description": "Reminder settings. Example: {\"useDefault\": false, \"overrides\": [{\"method\": \"email\", \"minutes\": 30}, {\"method\": \"popup\", \"minutes\": 10}]}"
                    },
                },
                "required": ["summary", "start_time", "end_time"],
            },
        ),
        Tool(
            name="calendar_update_event",
            description="Update an existing calendar event.",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "Event ID."},
                    "calendar_id": {"type": "string", "description": "Calendar ID.", "default": "primary"},
                    "summary": {"type": "string", "description": "New event title."},
                    "start_time": {"type": "string", "description": "New start time."},
                    "end_time": {"type": "string", "description": "New end time."},
                    "description": {"type": "string", "description": "New description."},
                    "location": {"type": "string", "description": "New location."},
                    "timezone": {"type": "string", "description": "Timezone.", "default": "UTC"},
                    "reminders": {
                        "type": "object",
                        "description": "Reminder settings. Example: {\"useDefault\": false, \"overrides\": [{\"method\": \"email\", \"minutes\": 30}, {\"method\": \"popup\", \"minutes\": 10}]}"
                    },
                },
                "required": ["event_id"],
            },
        ),
        Tool(
            name="calendar_delete_event",
            description="Delete a calendar event (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "Event ID to delete."},
                    "calendar_id": {"type": "string", "description": "Calendar ID.", "default": "primary"},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["event_id", "confirm"],
            },
        ),
        Tool(
            name="calendar_list_calendars",
            description="List all calendars.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="calendar_create_calendar",
            description="Create a new calendar.",
            inputSchema={
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Calendar name."},
                    "description": {"type": "string", "description": "Calendar description."},
                    "timezone": {"type": "string", "description": "Timezone.", "default": "UTC"},
                },
                "required": ["summary"],
            },
        ),
        Tool(
            name="calendar_add_attendees",
            description="Add attendees to an event (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "Event ID."},
                    "attendees": {"type": "array", "items": {"type": "string"}, "description": "Attendee emails."},
                    "calendar_id": {"type": "string", "description": "Calendar ID.", "default": "primary"},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["event_id", "attendees", "confirm"],
            },
        ),
        Tool(
            name="calendar_quick_add_event",
            description="Quick add event using natural language.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Natural language event description."},
                    "calendar_id": {"type": "string", "description": "Calendar ID.", "default": "primary"},
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="calendar_check_freebusy",
            description="Check free/busy information for calendars to see availability.",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_min": {"type": "string", "description": "Start time (RFC3339) to check availability."},
                    "time_max": {"type": "string", "description": "End time (RFC3339) to check availability."},
                    "calendar_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of calendar IDs to check. Defaults to ['primary']."
                    },
                    "timezone": {"type": "string", "description": "Timezone.", "default": "UTC"},
                },
                "required": ["time_min", "time_max"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "calendar_search_events": svc.search_events,
        "calendar_get_event": svc.get_event,
        "calendar_create_event": svc.create_event,
        "calendar_update_event": svc.update_event,
        "calendar_delete_event": svc.delete_event,
        "calendar_list_calendars": svc.list_calendars,
        "calendar_create_calendar": svc.create_calendar,
        "calendar_add_attendees": svc.add_attendees,
        "calendar_quick_add_event": svc.quick_add_event,
        "calendar_check_freebusy": svc.check_freebusy,
    }
    if name not in handlers:
        raise ValueError(f"Unknown tool: {name}")
    # Errors are not caught here: the MCP server turns any exception into an isError result.
    result = handlers[name](**arguments)
    return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def run() -> None:
    """Console-script entry point."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
