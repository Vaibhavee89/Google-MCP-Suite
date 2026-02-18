from __future__ import annotations

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_cloudlogging_mcp.service import CloudLoggingService

app = Server("google-cloudlogging-mcp")


def _svc() -> CloudLoggingService:
    return CloudLoggingService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="cloudlogging.list_logs",
            description="List recent log entries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 50},
                },
            },
        ),
        Tool(
            name="cloudlogging.query_logs",
            description="Query logs with a filter expression.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_str": {"type": "string", "description": "Log filter expression."},
                    "limit": {"type": "integer", "description": "Max results.", "default": 100},
                },
                "required": ["filter_str"],
            },
        ),
        Tool(
            name="cloudlogging.get_log_metrics",
            description="List log-based metrics.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "cloudlogging.list_logs": svc.list_logs,
        "cloudlogging.query_logs": svc.query_logs,
        "cloudlogging.get_log_metrics": svc.get_log_metrics,
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
