from __future__ import annotations

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_cloudrun_mcp.service import CloudRunService

app = Server("google-cloudrun-mcp")


def _svc() -> CloudRunService:
    return CloudRunService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="cloudrun.list_services",
            description="List Cloud Run services.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 50},
                },
            },
        ),
        Tool(
            name="cloudrun.get_service",
            description="Get Cloud Run service details.",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_name": {"type": "string", "description": "Service name."},
                },
                "required": ["service_name"],
            },
        ),
        Tool(
            name="cloudrun.list_revisions",
            description="List Cloud Run service revisions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_name": {"type": "string", "description": "Service name."},
                    "limit": {"type": "integer", "description": "Max results.", "default": 20},
                },
                "required": ["service_name"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "cloudrun.list_services": svc.list_services,
        "cloudrun.get_service": svc.get_service,
        "cloudrun.list_revisions": svc.list_revisions,
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
