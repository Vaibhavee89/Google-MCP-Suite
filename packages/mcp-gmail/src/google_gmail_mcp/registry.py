from __future__ import annotations

from typing import Any, Dict

from google_gmail_mcp.service import GmailService


TOOL_DEFINITIONS: list[Dict[str, Any]] = [
    {
        "name": "gmail.search_messages",
        "description": "Search Gmail messages by query string.",
        "parameters": {"query": "string", "limit": "int", "page_token": "string"},
    },
    {
        "name": "gmail.read_message",
        "description": "Read a Gmail message by id.",
        "parameters": {"message_id": "string", "format": "string"},
    },
]


def list_tools() -> list[Dict[str, Any]]:
    return TOOL_DEFINITIONS


def call_tool(name: str, **kwargs: Any) -> Dict[str, Any]:
    service = GmailService.from_config()
    handlers = {
        "gmail.search_messages": service.search_messages,
        "gmail.read_message": service.read_message,
    }
    if name not in handlers:
        raise ValueError(f"Unknown tool: {name}")
    return handlers[name](**kwargs)
