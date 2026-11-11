from __future__ import annotations

from typing import Any, Dict

from google_gcs_mcp.service import GCSService


TOOL_DEFINITIONS: list[Dict[str, Any]] = [
    {
        "name": "gcs_list_objects",
        "description": "List objects in a GCS bucket.",
        "parameters": {
            "bucket_name": "string",
            "prefix": "string",
            "limit": "int",
            "page_token": "string",
        },
    },
    {
        "name": "gcs_get_object_metadata",
        "description": "Get GCS object metadata.",
        "parameters": {"bucket_name": "string", "object_name": "string"},
    },
    {
        "name": "gcs_download_object",
        "description": "Download GCS object contents as base64.",
        "parameters": {"bucket_name": "string", "object_name": "string"},
    },
]


def list_tools() -> list[Dict[str, Any]]:
    return TOOL_DEFINITIONS


def call_tool(name: str, **kwargs: Any) -> Dict[str, Any]:
    service = GCSService.from_config()
    handlers = {
        "gcs_list_objects": service.list_objects,
        "gcs_get_object_metadata": service.get_object_metadata,
        "gcs_download_object": service.download_object,
    }
    if name not in handlers:
        raise ValueError(f"Unknown tool: {name}")
    return handlers[name](**kwargs)
