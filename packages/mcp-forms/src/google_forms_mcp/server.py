from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_forms_mcp.service import FormsService

app = Server("google-forms-mcp")


@lru_cache(maxsize=1)
def _svc() -> FormsService:
    """One service per process: config is read once and Google clients are reused."""
    return FormsService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="forms_get_form",
            description="Get form metadata and structure.",
            inputSchema={
                "type": "object",
                "properties": {
                    "form_id": {"type": "string", "description": "Form ID."},
                },
                "required": ["form_id"],
            },
        ),
        Tool(
            name="forms_list_responses",
            description="List form responses.",
            inputSchema={
                "type": "object",
                "properties": {
                    "form_id": {"type": "string", "description": "Form ID."},
                    "limit": {"type": "integer", "description": "Max results.", "default": 50},
                },
                "required": ["form_id"],
            },
        ),
        Tool(
            name="forms_get_response",
            description="Get a specific form response.",
            inputSchema={
                "type": "object",
                "properties": {
                    "form_id": {"type": "string", "description": "Form ID."},
                    "response_id": {"type": "string", "description": "Response ID."},
                },
                "required": ["form_id", "response_id"],
            },
        ),
        Tool(
            name="forms_create_form",
            description="Create a new Google Form (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Form title."},
                    "description": {"type": "string", "description": "Form description."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["title", "confirm"],
            },
        ),
        Tool(
            name="forms_add_text_question",
            description="Add a text question to a form (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "form_id": {"type": "string", "description": "Form ID."},
                    "question": {"type": "string", "description": "Question text."},
                    "required": {"type": "boolean", "description": "Is required.", "default": False},
                    "paragraph": {"type": "boolean", "description": "Paragraph text.", "default": False},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["form_id", "question", "confirm"],
            },
        ),
        Tool(
            name="forms_add_multiple_choice_question",
            description="Add a multiple choice question to a form (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "form_id": {"type": "string", "description": "Form ID."},
                    "question": {"type": "string", "description": "Question text."},
                    "options": {"type": "array", "items": {"type": "string"}, "description": "Answer options."},
                    "required": {"type": "boolean", "description": "Is required.", "default": False},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["form_id", "question", "options", "confirm"],
            },
        ),
        Tool(
            name="forms_add_checkbox_question",
            description="Add a checkbox question to a form (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "form_id": {"type": "string", "description": "Form ID."},
                    "question": {"type": "string", "description": "Question text."},
                    "options": {"type": "array", "items": {"type": "string"}, "description": "Checkbox options."},
                    "required": {"type": "boolean", "description": "Is required.", "default": False},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["form_id", "question", "options", "confirm"],
            },
        ),
        Tool(
            name="forms_update_form_info",
            description="Update form title and description (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "form_id": {"type": "string", "description": "Form ID."},
                    "title": {"type": "string", "description": "New title."},
                    "description": {"type": "string", "description": "New description."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["form_id", "confirm"],
            },
        ),
        Tool(
            name="forms_delete_item",
            description="Delete a question/item from a form (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "form_id": {"type": "string", "description": "Form ID."},
                    "item_id": {"type": "string", "description": "Item ID to delete."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["form_id", "item_id", "confirm"],
            },
        ),
        Tool(
            name="forms_update_settings",
            description="Update form settings (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "form_id": {"type": "string", "description": "Form ID."},
                    "collect_email": {"type": "boolean", "description": "Collect email addresses."},
                    "allow_response_edits": {"type": "boolean", "description": "Allow response edits."},
                    "quiz_mode": {"type": "boolean", "description": "Enable quiz mode."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["form_id", "confirm"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "forms_get_form": svc.get_form,
        "forms_list_responses": svc.list_responses,
        "forms_get_response": svc.get_response,
        "forms_create_form": svc.create_form,
        "forms_add_text_question": svc.add_text_question,
        "forms_add_multiple_choice_question": svc.add_multiple_choice_question,
        "forms_add_checkbox_question": svc.add_checkbox_question,
        "forms_update_form_info": svc.update_form_info,
        "forms_delete_item": svc.delete_item,
        "forms_update_settings": svc.update_settings,
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
