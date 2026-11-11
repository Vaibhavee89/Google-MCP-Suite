from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_drive_mcp.service import DriveService

app = Server("google-drive-mcp")


@lru_cache(maxsize=1)
def _svc() -> DriveService:
    """One service per process: config is read once and Google clients are reused."""
    return DriveService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="drive_search_files",
            description="Search Drive files by query string.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Drive search query (e.g. \"name contains 'report'\")."},
                    "limit": {"type": "integer", "description": "Max results to return.", "default": 25},
                    "page_token": {"type": "string", "description": "Pagination token."},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="drive_get_metadata",
            description="Get Drive file metadata by file ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "Drive file ID."},
                },
                "required": ["file_id"],
            },
        ),
        Tool(
            name="drive_read_text",
            description="Read Drive file contents as text (exports Google Docs to plain text).",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "Drive file ID."},
                },
                "required": ["file_id"],
            },
        ),
        Tool(
            name="drive_download",
            description="Download Drive file contents as base64.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "Drive file ID."},
                },
                "required": ["file_id"],
            },
        ),
        Tool(
            name="drive_list_children",
            description="List child files/folders inside a Drive folder.",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_id": {"type": "string", "description": "Drive folder ID."},
                    "limit": {"type": "integer", "description": "Max results.", "default": 50},
                    "page_token": {"type": "string", "description": "Pagination token."},
                },
                "required": ["folder_id"],
            },
        ),
        Tool(
            name="drive_get_permissions",
            description="List permissions on a Drive file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "Drive file ID."},
                },
                "required": ["file_id"],
            },
        ),
        Tool(
            name="drive_create_folder",
            description="Create a folder in Drive (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Folder name."},
                    "parent_id": {"type": "string", "description": "Parent folder ID."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["name", "confirm"],
            },
        ),
        Tool(
            name="drive_upload_file",
            description="Upload a file to Google Drive.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "File name."},
                    "content": {"type": "string", "description": "File content."},
                    "mime_type": {"type": "string", "description": "MIME type.", "default": "text/plain"},
                    "parent_id": {"type": "string", "description": "Parent folder ID."},
                },
                "required": ["name", "content"],
            },
        ),
        Tool(
            name="drive_move_file",
            description="Move a file to a different folder (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID to move."},
                    "new_parent_id": {"type": "string", "description": "New parent folder ID."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["file_id", "new_parent_id", "confirm"],
            },
        ),
        Tool(
            name="drive_copy_file",
            description="Copy a file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID to copy."},
                    "new_name": {"type": "string", "description": "New file name."},
                },
                "required": ["file_id"],
            },
        ),
        Tool(
            name="drive_delete_file",
            description="Permanently delete a file, bypassing trash (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID to delete."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["file_id", "confirm"],
            },
        ),
        Tool(
            name="drive_share_file",
            description="Share a file with a user (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID to share."},
                    "email": {"type": "string", "description": "User email address."},
                    "role": {"type": "string", "description": "Role (reader, writer, commenter).", "default": "reader"},
                    "send_notification": {"type": "boolean", "description": "Send email notification.", "default": True},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["file_id", "email", "confirm"],
            },
        ),
        Tool(
            name="drive_update_file_metadata",
            description="Update file metadata (name, description).",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID."},
                    "name": {"type": "string", "description": "New file name."},
                    "description": {"type": "string", "description": "New description."},
                },
                "required": ["file_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "drive_search_files": svc.search_files,
        "drive_get_metadata": svc.get_metadata,
        "drive_read_text": svc.read_text,
        "drive_download": svc.download,
        "drive_list_children": svc.list_children,
        "drive_get_permissions": svc.get_permissions,
        "drive_create_folder": svc.create_folder,
        "drive_upload_file": svc.upload_file,
        "drive_move_file": svc.move_file,
        "drive_copy_file": svc.copy_file,
        "drive_delete_file": svc.delete_file,
        "drive_share_file": svc.share_file,
        "drive_update_file_metadata": svc.update_file_metadata,
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
