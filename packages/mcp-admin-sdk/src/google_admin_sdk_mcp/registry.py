from __future__ import annotations

from typing import Any, Dict

from google_admin_sdk_mcp.service import AdminSDKService


TOOL_DEFINITIONS: list[Dict[str, Any]] = [
    {
        "name": "admin_list_users",
        "description": "List users in the Admin Directory.",
        "parameters": {
            "customer": "string",
            "domain": "string",
            "limit": "int",
            "page_token": "string",
        },
    },
    {
        "name": "admin_get_user",
        "description": "Get a user from the Admin Directory.",
        "parameters": {"user_key": "string"},
    },
]


def list_tools() -> list[Dict[str, Any]]:
    return TOOL_DEFINITIONS


def call_tool(name: str, **kwargs: Any) -> Dict[str, Any]:
    service = AdminSDKService.from_config()
    handlers = {
        "admin_list_users": service.list_users,
        "admin_get_user": service.get_user,
    }
    if name not in handlers:
        raise ValueError(f"Unknown tool: {name}")
    return handlers[name](**kwargs)
