from __future__ import annotations

from typing import Any, Dict

from google_drive_mcp.service import DriveService


TOOL_DEFINITIONS: list[Dict[str, Any]] = [
    {
        "name": "drive.search_files",
        "description": "Search Drive files by query string.",
        "parameters": {"query": "string", "limit": "int", "page_token": "string"},
    },
    {
        "name": "drive.get_metadata",
        "description": "Get Drive file metadata.",
        "parameters": {"file_id": "string"},
    },
    {
        "name": "drive.read_text",
        "description": "Read Drive file contents as text (exports Google Docs).",
        "parameters": {"file_id": "string"},
    },
    {
        "name": "drive.download",
        "description": "Download Drive file contents as base64.",
        "parameters": {"file_id": "string"},
    },
    {
        "name": "drive.list_children",
        "description": "List child files for a folder.",
        "parameters": {"folder_id": "string", "limit": "int", "page_token": "string"},
    },
    {
        "name": "drive.get_permissions",
        "description": "List Drive file permissions.",
        "parameters": {"file_id": "string"},
    },
    {
        "name": "drive.create_folder",
        "description": "Create a Drive folder.",
        "parameters": {"name": "string", "parent_id": "string", "confirm": "bool"},
    },
]


def list_tools() -> list[Dict[str, Any]]:
    return TOOL_DEFINITIONS


def call_tool(name: str, **kwargs: Any) -> Dict[str, Any]:
    service = DriveService.from_config()
    handlers = {
        "drive.search_files": service.search_files,
        "drive.get_metadata": service.get_metadata,
        "drive.read_text": service.read_text,
        "drive.download": service.download,
        "drive.list_children": service.list_children,
        "drive.get_permissions": service.get_permissions,
        "drive.create_folder": service.create_folder,
    }
    if name not in handlers:
        raise ValueError(f"Unknown tool: {name}")
    return handlers[name](**kwargs)
