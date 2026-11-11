from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_people_mcp.service import PeopleService

app = Server("google-people-mcp")


@lru_cache(maxsize=1)
def _svc() -> PeopleService:
    """One service per process: config is read once and Google clients are reused."""
    return PeopleService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="people_list_contacts",
            description="List contacts from Google Contacts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 100},
                    "page_token": {"type": "string", "description": "Pagination token."},
                },
            },
        ),
        Tool(
            name="people_get_contact",
            description="Get detailed information about a contact.",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_name": {"type": "string", "description": "Contact resource name (e.g., people/c123)."},
                },
                "required": ["resource_name"],
            },
        ),
        Tool(
            name="people_search_contacts",
            description="Search contacts by name, email, or phone.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query."},
                    "limit": {"type": "integer", "description": "Max results.", "default": 25},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="people_create_contact",
            description="Create a new contact (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "given_name": {"type": "string", "description": "First name."},
                    "family_name": {"type": "string", "description": "Last name."},
                    "emails": {"type": "array", "items": {"type": "string"}, "description": "Email addresses."},
                    "phones": {"type": "array", "items": {"type": "string"}, "description": "Phone numbers."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["given_name", "confirm"],
            },
        ),
        Tool(
            name="people_update_contact",
            description="Update an existing contact (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_name": {"type": "string", "description": "Contact resource name."},
                    "given_name": {"type": "string", "description": "New first name."},
                    "family_name": {"type": "string", "description": "New last name."},
                    "emails": {"type": "array", "items": {"type": "string"}, "description": "New email addresses."},
                    "phones": {"type": "array", "items": {"type": "string"}, "description": "New phone numbers."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["resource_name", "confirm"],
            },
        ),
        Tool(
            name="people_delete_contact",
            description="Delete a contact (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_name": {"type": "string", "description": "Contact resource name to delete."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["resource_name", "confirm"],
            },
        ),
        Tool(
            name="people_batch_create_contacts",
            description="Batch create multiple contacts (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "contacts": {"type": "array", "items": {"type": "object"}, "description": "Array of contact objects."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["contacts", "confirm"],
            },
        ),
        Tool(
            name="people_create_contact_group",
            description="Create a new contact group (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Group name."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["name", "confirm"],
            },
        ),
        Tool(
            name="people_add_contact_to_group",
            description="Add a contact to a group (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "group_resource_name": {"type": "string", "description": "Group resource name."},
                    "contact_resource_name": {"type": "string", "description": "Contact resource name."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["group_resource_name", "contact_resource_name", "confirm"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "people_list_contacts": svc.list_contacts,
        "people_get_contact": svc.get_contact,
        "people_search_contacts": svc.search_contacts,
        "people_create_contact": svc.create_contact,
        "people_update_contact": svc.update_contact,
        "people_delete_contact": svc.delete_contact,
        "people_batch_create_contacts": svc.batch_create_contacts,
        "people_create_contact_group": svc.create_contact_group,
        "people_add_contact_to_group": svc.add_contact_to_group,
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
