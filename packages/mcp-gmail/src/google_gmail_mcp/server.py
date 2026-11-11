from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_gmail_mcp.service import GmailService

app = Server("google-gmail-mcp")


@lru_cache(maxsize=1)
def _svc() -> GmailService:
    """One service per process: config is read once and Google clients are reused."""
    return GmailService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="gmail_search_messages",
            description="Search Gmail messages by query string.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Gmail search query."},
                    "limit": {"type": "integer", "description": "Max results.", "default": 25},
                    "page_token": {"type": "string", "description": "Pagination token."},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="gmail_read_message",
            description="Read a Gmail message by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "Gmail message ID."},
                    "format": {"type": "string", "description": "Response format (full, metadata, minimal).", "default": "full"},
                },
                "required": ["message_id"],
            },
        ),
        Tool(
            name="gmail_send_email",
            description="Send an email (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address."},
                    "subject": {"type": "string", "description": "Email subject."},
                    "body": {"type": "string", "description": "Email body."},
                    "cc": {"type": "string", "description": "CC email addresses."},
                    "bcc": {"type": "string", "description": "BCC email addresses."},
                    "html": {"type": "boolean", "description": "Send as HTML.", "default": False},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["to", "subject", "body", "confirm"],
            },
        ),
        Tool(
            name="gmail_create_draft",
            description="Create a draft email.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address."},
                    "subject": {"type": "string", "description": "Email subject."},
                    "body": {"type": "string", "description": "Email body."},
                    "cc": {"type": "string", "description": "CC email addresses."},
                    "html": {"type": "boolean", "description": "Draft as HTML.", "default": False},
                },
                "required": ["to", "subject", "body"],
            },
        ),
        Tool(
            name="gmail_reply_to_message",
            description="Reply to an email message (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "Message ID to reply to."},
                    "body": {"type": "string", "description": "Reply body."},
                    "html": {"type": "boolean", "description": "Reply as HTML.", "default": False},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["message_id", "body", "confirm"],
            },
        ),
        Tool(
            name="gmail_modify_labels",
            description="Add or remove labels from a message.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "Message ID."},
                    "add_labels": {"type": "array", "items": {"type": "string"}, "description": "Label IDs to add."},
                    "remove_labels": {"type": "array", "items": {"type": "string"}, "description": "Label IDs to remove."},
                },
                "required": ["message_id"],
            },
        ),
        Tool(
            name="gmail_trash_message",
            description="Move a message to trash (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "Message ID to trash."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["message_id", "confirm"],
            },
        ),
        Tool(
            name="gmail_delete_message",
            description="Permanently delete a message (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "Message ID to delete."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["message_id", "confirm"],
            },
        ),
        Tool(
            name="gmail_mark_as_read",
            description="Mark a message as read.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "Message ID."},
                },
                "required": ["message_id"],
            },
        ),
        Tool(
            name="gmail_mark_as_unread",
            description="Mark a message as unread.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "Message ID."},
                },
                "required": ["message_id"],
            },
        ),
        Tool(
            name="gmail_list_labels",
            description="List all Gmail labels.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="gmail_create_label",
            description="Create a new Gmail label.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Label name."},
                    "label_list_visibility": {"type": "string", "description": "Visibility in label list.", "default": "labelShow"},
                    "message_list_visibility": {"type": "string", "description": "Visibility in message list.", "default": "show"},
                },
                "required": ["name"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "gmail_search_messages": svc.search_messages,
        "gmail_read_message": svc.read_message,
        "gmail_send_email": svc.send_email,
        "gmail_create_draft": svc.create_draft,
        "gmail_reply_to_message": svc.reply_to_message,
        "gmail_modify_labels": svc.modify_labels,
        "gmail_trash_message": svc.trash_message,
        "gmail_delete_message": svc.delete_message,
        "gmail_mark_as_read": svc.mark_as_read,
        "gmail_mark_as_unread": svc.mark_as_unread,
        "gmail_list_labels": svc.list_labels,
        "gmail_create_label": svc.create_label,
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
