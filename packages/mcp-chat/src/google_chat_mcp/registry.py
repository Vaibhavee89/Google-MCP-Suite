from __future__ import annotations

from typing import Any, Dict

from google_chat_mcp.service import ChatService


TOOL_DEFINITIONS: list[Dict[str, Any]] = [
    {
        "name": "chat.list_spaces",
        "description": "List Google Chat spaces.",
        "parameters": {"limit": "int", "page_token": "string"},
    },
    {
        "name": "chat.search_messages",
        "description": "Search messages in a Google Chat space.",
        "parameters": {
            "space": "string",
            "query": "string",
            "limit": "int",
            "page_token": "string",
        },
    },
]


def list_tools() -> list[Dict[str, Any]]:
    return TOOL_DEFINITIONS


def call_tool(name: str, **kwargs: Any) -> Dict[str, Any]:
    service = ChatService.from_config()
    handlers = {
        "chat.list_spaces": service.list_spaces,
        "chat.search_messages": service.search_messages,
    }
    if name not in handlers:
        raise ValueError(f"Unknown tool: {name}")
    return handlers[name](**kwargs)
