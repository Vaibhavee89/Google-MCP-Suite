from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_tasks_mcp.service import TasksService

app = Server("google-tasks-mcp")


@lru_cache(maxsize=1)
def _svc() -> TasksService:
    """One service per process: config is read once and Google clients are reused."""
    return TasksService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="tasks_list_task_lists",
            description="List all task lists.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 50},
                },
            },
        ),
        Tool(
            name="tasks_list_tasks",
            description="List tasks in a task list.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tasklist_id": {"type": "string", "description": "Task list ID."},
                    "limit": {"type": "integer", "description": "Max results.", "default": 100},
                    "show_completed": {"type": "boolean", "description": "Include completed tasks.", "default": False},
                },
                "required": ["tasklist_id"],
            },
        ),
        Tool(
            name="tasks_get_task",
            description="Get a specific task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tasklist_id": {"type": "string", "description": "Task list ID."},
                    "task_id": {"type": "string", "description": "Task ID."},
                },
                "required": ["tasklist_id", "task_id"],
            },
        ),
        Tool(
            name="tasks_create_task",
            description="Create a new task in a task list (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "tasklist_id": {"type": "string", "description": "Task list ID."},
                    "title": {"type": "string", "description": "Task title."},
                    "notes": {"type": "string", "description": "Task notes/description."},
                    "due": {"type": "string", "description": "Due date (RFC 3339 timestamp)."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["tasklist_id", "title", "confirm"],
            },
        ),
        Tool(
            name="tasks_update_task",
            description="Update an existing task (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "tasklist_id": {"type": "string", "description": "Task list ID."},
                    "task_id": {"type": "string", "description": "Task ID."},
                    "title": {"type": "string", "description": "New task title."},
                    "notes": {"type": "string", "description": "New task notes."},
                    "due": {"type": "string", "description": "New due date."},
                    "status": {"type": "string", "description": "Task status (needsAction, completed)."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["tasklist_id", "task_id", "confirm"],
            },
        ),
        Tool(
            name="tasks_delete_task",
            description="Delete a task (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "tasklist_id": {"type": "string", "description": "Task list ID."},
                    "task_id": {"type": "string", "description": "Task ID to delete."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["tasklist_id", "task_id", "confirm"],
            },
        ),
        Tool(
            name="tasks_complete_task",
            description="Mark a task as completed (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "tasklist_id": {"type": "string", "description": "Task list ID."},
                    "task_id": {"type": "string", "description": "Task ID to complete."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["tasklist_id", "task_id", "confirm"],
            },
        ),
        Tool(
            name="tasks_create_task_list",
            description="Create a new task list (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task list title."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["title", "confirm"],
            },
        ),
        Tool(
            name="tasks_delete_task_list",
            description="Delete a task list (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "tasklist_id": {"type": "string", "description": "Task list ID to delete."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["tasklist_id", "confirm"],
            },
        ),
        Tool(
            name="tasks_move_task",
            description="Move a task to a different position (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "tasklist_id": {"type": "string", "description": "Task list ID."},
                    "task_id": {"type": "string", "description": "Task ID to move."},
                    "parent": {"type": "string", "description": "New parent task ID."},
                    "previous": {"type": "string", "description": "Previous sibling task ID."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["tasklist_id", "task_id", "confirm"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "tasks_list_task_lists": svc.list_task_lists,
        "tasks_list_tasks": svc.list_tasks,
        "tasks_get_task": svc.get_task,
        "tasks_create_task": svc.create_task,
        "tasks_update_task": svc.update_task,
        "tasks_delete_task": svc.delete_task,
        "tasks_complete_task": svc.complete_task,
        "tasks_create_task_list": svc.create_task_list,
        "tasks_delete_task_list": svc.delete_task_list,
        "tasks_move_task": svc.move_task,
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
