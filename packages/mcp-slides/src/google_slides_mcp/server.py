from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_slides_mcp.service import SlidesService

app = Server("google-slides-mcp")


@lru_cache(maxsize=1)
def _svc() -> SlidesService:
    """One service per process: config is read once and Google clients are reused."""
    return SlidesService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="slides_get_presentation",
            description="Get presentation metadata and structure.",
            inputSchema={
                "type": "object",
                "properties": {
                    "presentation_id": {"type": "string", "description": "Presentation ID."},
                },
                "required": ["presentation_id"],
            },
        ),
        Tool(
            name="slides_get_slide_content",
            description="Get content of a specific slide.",
            inputSchema={
                "type": "object",
                "properties": {
                    "presentation_id": {"type": "string", "description": "Presentation ID."},
                    "slide_id": {"type": "string", "description": "Slide object ID."},
                },
                "required": ["presentation_id", "slide_id"],
            },
        ),
        Tool(
            name="slides_list_presentations",
            description="List Google Slides presentations from Drive.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 25},
                    "page_token": {"type": "string", "description": "Pagination token."},
                },
            },
        ),
        Tool(
            name="slides_extract_text",
            description="Extract all text content from a presentation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "presentation_id": {"type": "string", "description": "Presentation ID."},
                },
                "required": ["presentation_id"],
            },
        ),
        Tool(
            name="slides_create_slide",
            description="Create a new slide in a presentation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "presentation_id": {"type": "string", "description": "Presentation ID."},
                    "title": {"type": "string", "description": "Optional title for the slide."},
                    "insertion_index": {"type": "integer", "description": "Position to insert (null for end)."},
                    "layout": {"type": "string", "description": "Slide layout (BLANK, TITLE, TITLE_AND_BODY, etc.)", "default": "BLANK"},
                },
                "required": ["presentation_id"],
            },
        ),
        Tool(
            name="slides_add_text_to_slide",
            description="Add a text box to an existing slide.",
            inputSchema={
                "type": "object",
                "properties": {
                    "presentation_id": {"type": "string", "description": "Presentation ID."},
                    "slide_id": {"type": "string", "description": "Slide object ID."},
                    "text": {"type": "string", "description": "Text content to add."},
                    "x": {"type": "number", "description": "X position in points.", "default": 50},
                    "y": {"type": "number", "description": "Y position in points.", "default": 50},
                    "width": {"type": "number", "description": "Width in points.", "default": 400},
                    "height": {"type": "number", "description": "Height in points.", "default": 50},
                },
                "required": ["presentation_id", "slide_id", "text"],
            },
        ),
        Tool(
            name="slides_update_text",
            description="Update text in an existing text box or shape.",
            inputSchema={
                "type": "object",
                "properties": {
                    "presentation_id": {"type": "string", "description": "Presentation ID."},
                    "shape_id": {"type": "string", "description": "Shape/text box object ID."},
                    "new_text": {"type": "string", "description": "New text content."},
                },
                "required": ["presentation_id", "shape_id", "new_text"],
            },
        ),
        Tool(
            name="slides_delete_slide",
            description="Delete a slide from a presentation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "presentation_id": {"type": "string", "description": "Presentation ID."},
                    "slide_id": {"type": "string", "description": "Slide object ID to delete."},
                },
                "required": ["presentation_id", "slide_id"],
            },
        ),
        Tool(
            name="slides_create_presentation",
            description="Create a new presentation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title for the new presentation."},
                },
                "required": ["title"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "slides_get_presentation": svc.get_presentation,
        "slides_get_slide_content": svc.get_slide_content,
        "slides_list_presentations": svc.list_presentations,
        "slides_extract_text": svc.extract_text,
        "slides_create_slide": svc.create_slide,
        "slides_add_text_to_slide": svc.add_text_to_slide,
        "slides_update_text": svc.update_text,
        "slides_delete_slide": svc.delete_slide,
        "slides_create_presentation": svc.create_presentation,
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
