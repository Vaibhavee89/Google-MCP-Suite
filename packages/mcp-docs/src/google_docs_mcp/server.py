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
        Tool(
            name="docs.create_document",
            description="Create a new Google Doc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Document title."},
                },
                "required": ["title"],
            },
        ),
        Tool(
            name="docs.insert_text",
            description="Insert text at a specific position.",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document ID."},
                    "text": {"type": "string", "description": "Text to insert."},
                    "index": {"type": "integer", "description": "Position index.", "default": 1},
                },
                "required": ["document_id", "text"],
            },
        ),
        Tool(
            name="docs.delete_text",
            description="Delete text from a document.",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document ID."},
                    "start_index": {"type": "integer", "description": "Start index."},
                    "end_index": {"type": "integer", "description": "End index."},
                },
                "required": ["document_id", "start_index", "end_index"],
            },
        ),
        Tool(
            name="docs.replace_text",
            description="Replace all occurrences of text.",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document ID."},
                    "old_text": {"type": "string", "description": "Text to replace."},
                    "new_text": {"type": "string", "description": "Replacement text."},
                },
                "required": ["document_id", "old_text", "new_text"],
            },
        ),
        Tool(
            name="docs.append_text",
            description="Append text to the end of a document.",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document ID."},
                    "text": {"type": "string", "description": "Text to append."},
                },
                "required": ["document_id", "text"],
            },
        ),
        Tool(
            name="docs.format_text",
            description="Format text in a document.",
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
                },
                "required": ["document_id", "start_index", "end_index"],
            },
        ),
        Tool(
            name="docs.insert_image",
            description="Insert an image into a document.",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document ID."},
                    "image_url": {"type": "string", "description": "Image URL."},
                    "index": {"type": "integer", "description": "Position index.", "default": 1},
                },
                "required": ["document_id", "image_url"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "docs.get_document": svc.get_document,
        "docs.export_text": svc.export_text,
        "docs.create_document": svc.create_document,
        "docs.insert_text": svc.insert_text,
        "docs.delete_text": svc.delete_text,
        "docs.replace_text": svc.replace_text,
        "docs.append_text": svc.append_text,
        "docs.format_text": svc.format_text,
        "docs.insert_image": svc.insert_image,
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
