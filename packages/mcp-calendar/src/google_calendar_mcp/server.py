from __future__ import annotations

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_calendar_mcp.service import CalendarService

app = Server("google-calendar-mcp")


def _svc() -> CalendarService:
    return CalendarService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="calendar.search_events",
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
            name="calendar.get_event",
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
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "calendar.search_events": svc.search_events,
        "calendar.get_event": svc.get_event,
    }
    if name not in handlers:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    try:
        result = handlers[name](**arguments)
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
    except Exception as exc:
        return [TextContent(type="text", text=f"Error: {exc}")]


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
