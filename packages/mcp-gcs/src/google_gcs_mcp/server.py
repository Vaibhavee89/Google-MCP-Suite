from __future__ import annotations

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_gcs_mcp.service import GCSService

app = Server("google-gcs-mcp")


def _svc() -> GCSService:
    return GCSService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="gcs.list_objects",
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
            name="gcs.get_object_metadata",
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
            name="gcs.download_object",
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
        "gcs.list_objects": svc.list_objects,
        "gcs.get_object_metadata": svc.get_object_metadata,
        "gcs.download_object": svc.download_object,
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
