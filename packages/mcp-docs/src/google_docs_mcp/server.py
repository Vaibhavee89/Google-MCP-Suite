from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_docs_mcp.service import DocsService

app = Server("google-docs-mcp")


@lru_cache(maxsize=1)
def _svc() -> DocsService:
    """One service per process: config is read once and Google clients are reused."""
    return DocsService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="docs_get_document",
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
            name="docs_export_text",
            description="Export a Google Docs document as plain text.",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Google Docs document ID."},
                },
                "required": ["document_id"],
            },
        ),
        Tool(
            name="docs_create_document",
            description="Create a new Google Doc (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Document title."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["title", "confirm"],
            },
        ),
        Tool(
            name="docs_insert_text",
            description="Insert text at a specific position (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document ID."},
                    "text": {"type": "string", "description": "Text to insert."},
                    "index": {"type": "integer", "description": "Position index.", "default": 1},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["document_id", "text", "confirm"],
            },
        ),
        Tool(
            name="docs_delete_text",
            description="Delete text from a document (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document ID."},
                    "start_index": {"type": "integer", "description": "Start index."},
                    "end_index": {"type": "integer", "description": "End index."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["document_id", "start_index", "end_index", "confirm"],
            },
        ),
        Tool(
            name="docs_replace_text",
            description="Replace all occurrences of text (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document ID."},
                    "old_text": {"type": "string", "description": "Text to replace."},
                    "new_text": {"type": "string", "description": "Replacement text."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["document_id", "old_text", "new_text", "confirm"],
            },
        ),
        Tool(
            name="docs_append_text",
            description="Append text to the end of a document (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document ID."},
                    "text": {"type": "string", "description": "Text to append."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["document_id", "text", "confirm"],
            },
        ),
        Tool(
            name="docs_format_text",
            description="Format text in a document (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document ID."},
                    "start_index": {"type": "integer", "description": "Start index."},
                    "end_index": {"type": "integer", "description": "End index."},
                    "bold": {"type": "boolean", "description": "Make text bold."},
                    "italic": {"type": "boolean", "description": "Make text italic."},
                    "underline": {"type": "boolean", "description": "Underline text."},
                    "font_size": {"type": "integer", "description": "Font size in points."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["document_id", "start_index", "end_index", "confirm"],
            },
        ),
        Tool(
            name="docs_insert_image",
            description="Insert an image into a document (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document ID."},
                    "image_url": {"type": "string", "description": "Image URL."},
                    "index": {"type": "integer", "description": "Position index.", "default": 1},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["document_id", "image_url", "confirm"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "docs_get_document": svc.get_document,
        "docs_export_text": svc.export_text,
        "docs_create_document": svc.create_document,
        "docs_insert_text": svc.insert_text,
        "docs_delete_text": svc.delete_text,
        "docs_replace_text": svc.replace_text,
        "docs_append_text": svc.append_text,
        "docs_format_text": svc.format_text,
        "docs_insert_image": svc.insert_image,
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
