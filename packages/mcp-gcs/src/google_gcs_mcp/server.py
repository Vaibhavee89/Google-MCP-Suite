from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_gcs_mcp.service import GCSService

app = Server("google-gcs-mcp")


@lru_cache(maxsize=1)
def _svc() -> GCSService:
    """One service per process: config is read once and Google clients are reused."""
    return GCSService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="gcs_list_objects",
            description="List objects in a GCS bucket.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {"type": "string", "description": "GCS bucket name."},
                    "prefix": {"type": "string", "description": "Object name prefix filter."},
                    "limit": {"type": "integer", "description": "Max results.", "default": 100},
                    "page_token": {"type": "string", "description": "Pagination token."},
                },
                "required": ["bucket_name"],
            },
        ),
        Tool(
            name="gcs_get_object_metadata",
            description="Get GCS object metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {"type": "string", "description": "GCS bucket name."},
                    "object_name": {"type": "string", "description": "Object name (path)."},
                },
                "required": ["bucket_name", "object_name"],
            },
        ),
        Tool(
            name="gcs_download_object",
            description="Download GCS object contents as base64.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {"type": "string", "description": "GCS bucket name."},
                    "object_name": {"type": "string", "description": "Object name (path)."},
                },
                "required": ["bucket_name", "object_name"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "gcs_list_objects": svc.list_objects,
        "gcs_get_object_metadata": svc.get_object_metadata,
        "gcs_download_object": svc.download_object,
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
