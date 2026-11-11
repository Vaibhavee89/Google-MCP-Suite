from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_cloudrun_mcp.service import CloudRunService

app = Server("google-cloudrun-mcp")


@lru_cache(maxsize=1)
def _svc() -> CloudRunService:
    """One service per process: config is read once and Google clients are reused."""
    return CloudRunService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="cloudrun_list_services",
            description="List Cloud Run services.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 50},
                },
            },
        ),
        Tool(
            name="cloudrun_get_service",
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
            name="cloudrun_list_revisions",
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
        "cloudrun_list_services": svc.list_services,
        "cloudrun_get_service": svc.get_service,
        "cloudrun_list_revisions": svc.list_revisions,
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
