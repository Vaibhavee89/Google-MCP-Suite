from __future__ import annotations

from typing import Any, Dict

from google_calendar_mcp.service import CalendarService


TOOL_DEFINITIONS: list[Dict[str, Any]] = [
    {
        "name": "calendar.search_events",
        "description": "Search Calendar events with optional query/time filters.",
        "parameters": {
            "calendar_id": "string",
            "query": "string",
            "time_min": "string",
            "time_max": "string",
            "limit": "int",
            "page_token": "string",
        },
    },
    {
        "name": "calendar.get_event",
        "description": "Get a Calendar event by id.",
        "parameters": {"event_id": "string", "calendar_id": "string"},
    },
]


def list_tools() -> list[Dict[str, Any]]:
    return TOOL_DEFINITIONS


def call_tool(name: str, **kwargs: Any) -> Dict[str, Any]:
    service = CalendarService.from_config()
    handlers = {
        "calendar.search_events": service.search_events,
        "calendar.get_event": service.get_event,
    }
    if name not in handlers:
        raise ValueError(f"Unknown tool: {name}")
    return handlers[name](**kwargs)
