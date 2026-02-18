from __future__ import annotations

from typing import Any, Dict

from google_docs_mcp.service import DocsService


TOOL_DEFINITIONS: list[Dict[str, Any]] = [
    {
        "name": "docs.get_document",
        "description": "Get a Docs document payload.",
        "parameters": {"document_id": "string"},
    },
    {
        "name": "docs.export_text",
        "description": "Export a Docs document as plain text.",
        "parameters": {"document_id": "string"},
    },
]


def list_tools() -> list[Dict[str, Any]]:
    return TOOL_DEFINITIONS


def call_tool(name: str, **kwargs: Any) -> Dict[str, Any]:
    service = DocsService.from_config()
    handlers = {
        "docs.get_document": service.get_document,
        "docs.export_text": service.export_text,
    }
    if name not in handlers:
        raise ValueError(f"Unknown tool: {name}")
    return handlers[name](**kwargs)
