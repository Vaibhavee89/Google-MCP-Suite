from __future__ import annotations

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_tasks_mcp.service import TasksService

app = Server("google-tasks-mcp")


def _svc() -> TasksService:
    return TasksService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="tasks.list_task_lists",
            description="List all task lists.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 50},
                },
            },
        ),
        Tool(
            name="tasks.list_tasks",
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
            name="tasks.get_task",
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
            name="tasks.create_task",
            description="Create a new task in a task list.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tasklist_id": {"type": "string", "description": "Task list ID."},
                    "title": {"type": "string", "description": "Task title."},
                    "notes": {"type": "string", "description": "Task notes/description."},
                    "due": {"type": "string", "description": "Due date (RFC 3339 timestamp)."},
                },
                "required": ["tasklist_id", "title"],
            },
        ),
        Tool(
            name="tasks.update_task",
            description="Update an existing task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tasklist_id": {"type": "string", "description": "Task list ID."},
                    "task_id": {"type": "string", "description": "Task ID."},
                    "title": {"type": "string", "description": "New task title."},
                    "notes": {"type": "string", "description": "New task notes."},
                    "due": {"type": "string", "description": "New due date."},
                    "status": {"type": "string", "description": "Task status (needsAction, completed)."},
                },
                "required": ["tasklist_id", "task_id"],
            },
        ),
        Tool(
            name="tasks.delete_task",
            description="Delete a task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tasklist_id": {"type": "string", "description": "Task list ID."},
                    "task_id": {"type": "string", "description": "Task ID to delete."},
                },
                "required": ["tasklist_id", "task_id"],
            },
        ),
        Tool(
            name="tasks.complete_task",
            description="Mark a task as completed.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tasklist_id": {"type": "string", "description": "Task list ID."},
                    "task_id": {"type": "string", "description": "Task ID to complete."},
                },
                "required": ["tasklist_id", "task_id"],
            },
        ),
        Tool(
            name="tasks.create_task_list",
            description="Create a new task list.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task list title."},
                },
                "required": ["title"],
            },
        ),
        Tool(
            name="tasks.delete_task_list",
            description="Delete a task list.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tasklist_id": {"type": "string", "description": "Task list ID to delete."},
                },
                "required": ["tasklist_id"],
            },
        ),
        Tool(
            name="tasks.move_task",
            description="Move a task to a different position.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tasklist_id": {"type": "string", "description": "Task list ID."},
                    "task_id": {"type": "string", "description": "Task ID to move."},
                    "parent": {"type": "string", "description": "New parent task ID."},
                    "previous": {"type": "string", "description": "Previous sibling task ID."},
                },
                "required": ["tasklist_id", "task_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "tasks.list_task_lists": svc.list_task_lists,
        "tasks.list_tasks": svc.list_tasks,
        "tasks.get_task": svc.get_task,
        "tasks.create_task": svc.create_task,
        "tasks.update_task": svc.update_task,
        "tasks.delete_task": svc.delete_task,
        "tasks.complete_task": svc.complete_task,
        "tasks.create_task_list": svc.create_task_list,
        "tasks.delete_task_list": svc.delete_task_list,
        "tasks.move_task": svc.move_task,
    }
    if name not in handlers:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    try:
        result = handlers[name](**arguments)
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
    except Exception as exc:
        return [TextContent(type="text", text=f"Error: {exc}")]


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
