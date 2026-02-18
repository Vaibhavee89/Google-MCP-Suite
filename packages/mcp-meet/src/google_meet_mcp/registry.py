from __future__ import annotations

from typing import Any, Dict

from google_meet_mcp.service import MeetService


TOOL_DEFINITIONS: list[Dict[str, Any]] = [
    {
        "name": "meet.list_activities",
        "description": "List Google Meet audit activities via Admin Reports.",
        "parameters": {
            "user_key": "string",
            "start_time": "string",
            "end_time": "string",
            "limit": "int",
            "page_token": "string",
        },
    },
    {
        "name": "meet.get_activity",
        "description": "Get a specific Meet audit activity.",
        "parameters": {"activity_id": "string", "user_key": "string"},
    },
]


def list_tools() -> list[Dict[str, Any]]:
    return TOOL_DEFINITIONS


def call_tool(name: str, **kwargs: Any) -> Dict[str, Any]:
    service = MeetService.from_config()
    handlers = {
        "meet.list_activities": service.list_activities,
        "meet.get_activity": service.get_activity,
    }
    if name not in handlers:
        raise ValueError(f"Unknown tool: {name}")
    return handlers[name](**kwargs)
