from __future__ import annotations

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_docs_mcp.service import DocsService

app = Server("google-docs-mcp")


def _svc() -> DocsService:
    return DocsService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="docs.get_document",
            description="Get a Google Docs document payload (structured JSON).",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Google Docs document ID."},
                },
                "required": ["document_id"],
            },
        ),
        Tool(
            name="docs.export_text",
            description="Export a Google Docs document as plain text.",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Google Docs document ID."},
                },
                "required": ["document_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "docs.get_document": svc.get_document,
        "docs.export_text": svc.export_text,
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
