from __future__ import annotations

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_admin_sdk_mcp.service import AdminSDKService

app = Server("google-admin-sdk-mcp")


def _svc() -> AdminSDKService:
    return AdminSDKService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="admin.list_users",
            description="List users in the Google Admin Directory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer": {"type": "string", "description": "Customer ID or 'my_customer'.", "default": "my_customer"},
                    "domain": {"type": "string", "description": "Domain to filter users."},
                    "limit": {"type": "integer", "description": "Max results.", "default": 25},
                    "page_token": {"type": "string", "description": "Pagination token."},
                },
            },
        ),
        Tool(
            name="admin.get_user",
            description="Get a user from the Google Admin Directory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_key": {"type": "string", "description": "User email or ID."},
                },
                "required": ["user_key"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "admin.list_users": svc.list_users,
        "admin.get_user": svc.get_user,
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
