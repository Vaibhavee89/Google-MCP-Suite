from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_cloudlogging_mcp.service import CloudLoggingService

app = Server("google-cloudlogging-mcp")


@lru_cache(maxsize=1)
def _svc() -> CloudLoggingService:
    """One service per process: config is read once and Google clients are reused."""
    return CloudLoggingService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="cloudlogging_list_logs",
            description="List recent log entries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 50},
                },
            },
        ),
        Tool(
            name="cloudlogging_query_logs",
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
            name="cloudlogging_get_log_metrics",
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
        "cloudlogging_list_logs": svc.list_logs,
        "cloudlogging_query_logs": svc.query_logs,
        "cloudlogging_get_log_metrics": svc.get_log_metrics,
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
