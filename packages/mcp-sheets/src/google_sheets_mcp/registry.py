from __future__ import annotations

from typing import Any, Dict

from google_sheets_mcp.service import SheetsService


TOOL_DEFINITIONS: list[Dict[str, Any]] = [
    {
        "name": "sheets.read_range",
        "description": "Read values from a Sheet range (A1 notation).",
        "parameters": {
            "spreadsheet_id": "string",
            "range_a1": "string",
            "major_dimension": "string",
            "value_render_option": "string",
        },
    },
    {
        "name": "sheets.get_metadata",
        "description": "Get spreadsheet metadata.",
        "parameters": {"spreadsheet_id": "string"},
    },
]


def list_tools() -> list[Dict[str, Any]]:
    return TOOL_DEFINITIONS


def call_tool(name: str, **kwargs: Any) -> Dict[str, Any]:
    service = SheetsService.from_config()
    handlers = {
        "sheets.read_range": service.read_range,
        "sheets.get_metadata": service.get_metadata,
    }
    if name not in handlers:
        raise ValueError(f"Unknown tool: {name}")
    return handlers[name](**kwargs)
