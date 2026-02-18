from __future__ import annotations

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_forms_mcp.service import FormsService

app = Server("google-forms-mcp")


def _svc() -> FormsService:
    return FormsService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="forms.get_form",
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
            name="forms.list_responses",
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
            name="forms.get_response",
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
            name="forms.create_form",
            description="Create a new Google Form.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Form title."},
                    "description": {"type": "string", "description": "Form description."},
                },
                "required": ["title"],
            },
        ),
        Tool(
            name="forms.add_text_question",
            description="Add a text question to a form.",
            inputSchema={
                "type": "object",
                "properties": {
                    "form_id": {"type": "string", "description": "Form ID."},
                    "question": {"type": "string", "description": "Question text."},
                    "required": {"type": "boolean", "description": "Is required.", "default": False},
                    "paragraph": {"type": "boolean", "description": "Paragraph text.", "default": False},
                },
                "required": ["form_id", "question"],
            },
        ),
        Tool(
            name="forms.add_multiple_choice_question",
            description="Add a multiple choice question to a form.",
            inputSchema={
                "type": "object",
                "properties": {
                    "form_id": {"type": "string", "description": "Form ID."},
                    "question": {"type": "string", "description": "Question text."},
                    "options": {"type": "array", "items": {"type": "string"}, "description": "Answer options."},
                    "required": {"type": "boolean", "description": "Is required.", "default": False},
                },
                "required": ["form_id", "question", "options"],
            },
        ),
        Tool(
            name="forms.add_checkbox_question",
            description="Add a checkbox question to a form.",
            inputSchema={
                "type": "object",
                "properties": {
                    "form_id": {"type": "string", "description": "Form ID."},
                    "question": {"type": "string", "description": "Question text."},
                    "options": {"type": "array", "items": {"type": "string"}, "description": "Checkbox options."},
                    "required": {"type": "boolean", "description": "Is required.", "default": False},
                },
                "required": ["form_id", "question", "options"],
            },
        ),
        Tool(
            name="forms.update_form_info",
            description="Update form title and description.",
            inputSchema={
                "type": "object",
                "properties": {
                    "form_id": {"type": "string", "description": "Form ID."},
                    "title": {"type": "string", "description": "New title."},
                    "description": {"type": "string", "description": "New description."},
                },
                "required": ["form_id"],
            },
        ),
        Tool(
            name="forms.delete_item",
            description="Delete a question/item from a form.",
            inputSchema={
                "type": "object",
                "properties": {
                    "form_id": {"type": "string", "description": "Form ID."},
                    "item_id": {"type": "string", "description": "Item ID to delete."},
                },
                "required": ["form_id", "item_id"],
            },
        ),
        Tool(
            name="forms.update_settings",
            description="Update form settings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "form_id": {"type": "string", "description": "Form ID."},
                    "collect_email": {"type": "boolean", "description": "Collect email addresses."},
                    "allow_response_edits": {"type": "boolean", "description": "Allow response edits."},
                    "quiz_mode": {"type": "boolean", "description": "Enable quiz mode."},
                },
                "required": ["form_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "forms.get_form": svc.get_form,
        "forms.list_responses": svc.list_responses,
        "forms.get_response": svc.get_response,
        "forms.create_form": svc.create_form,
        "forms.add_text_question": svc.add_text_question,
        "forms.add_multiple_choice_question": svc.add_multiple_choice_question,
        "forms.add_checkbox_question": svc.add_checkbox_question,
        "forms.update_form_info": svc.update_form_info,
        "forms.delete_item": svc.delete_item,
        "forms.update_settings": svc.update_settings,
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
