from __future__ import annotations

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_slides_mcp.service import SlidesService

app = Server("google-slides-mcp")


def _svc() -> SlidesService:
    return SlidesService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="slides.get_presentation",
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
            name="slides.get_slide_content",
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
            name="slides.list_presentations",
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
            name="slides.extract_text",
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
            name="slides.create_slide",
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
            name="slides.add_text_to_slide",
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
            name="slides.update_text",
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
            name="slides.delete_slide",
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
            name="slides.create_presentation",
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
        "slides.get_presentation": svc.get_presentation,
        "slides.get_slide_content": svc.get_slide_content,
        "slides.list_presentations": svc.list_presentations,
        "slides.extract_text": svc.extract_text,
        "slides.create_slide": svc.create_slide,
        "slides.add_text_to_slide": svc.add_text_to_slide,
        "slides.update_text": svc.update_text,
        "slides.delete_slide": svc.delete_slide,
        "slides.create_presentation": svc.create_presentation,
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
