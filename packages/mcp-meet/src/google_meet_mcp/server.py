from __future__ import annotations

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_meet_mcp.service import MeetService

app = Server("google-meet-mcp")


def _svc() -> MeetService:
    return MeetService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="meet.list_activities",
            description="List Google Meet audit activities via Admin Reports.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_key": {"type": "string", "description": "User key (email or 'all').", "default": "all"},
                    "start_time": {"type": "string", "description": "Start time (RFC3339)."},
                    "end_time": {"type": "string", "description": "End time (RFC3339)."},
                    "limit": {"type": "integer", "description": "Max results.", "default": 25},
                    "page_token": {"type": "string", "description": "Pagination token."},
                },
            },
        ),
        Tool(
            name="meet.get_activity",
            description="Get a specific Meet audit activity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "activity_id": {"type": "string", "description": "Activity ID."},
                    "user_key": {"type": "string", "description": "User key.", "default": "all"},
                },
                "required": ["activity_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "meet.list_activities": svc.list_activities,
        "meet.get_activity": svc.get_activity,
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
