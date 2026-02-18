from __future__ import annotations

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_people_mcp.service import PeopleService

app = Server("google-people-mcp")


def _svc() -> PeopleService:
    return PeopleService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="people.list_contacts",
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
            name="people.get_contact",
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
            name="people.search_contacts",
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
            name="people.create_contact",
            description="Create a new contact.",
            inputSchema={
                "type": "object",
                "properties": {
                    "given_name": {"type": "string", "description": "First name."},
                    "family_name": {"type": "string", "description": "Last name."},
                    "emails": {"type": "array", "items": {"type": "string"}, "description": "Email addresses."},
                    "phones": {"type": "array", "items": {"type": "string"}, "description": "Phone numbers."},
                },
                "required": ["given_name"],
            },
        ),
        Tool(
            name="people.update_contact",
            description="Update an existing contact.",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_name": {"type": "string", "description": "Contact resource name."},
                    "given_name": {"type": "string", "description": "New first name."},
                    "family_name": {"type": "string", "description": "New last name."},
                    "emails": {"type": "array", "items": {"type": "string"}, "description": "New email addresses."},
                    "phones": {"type": "array", "items": {"type": "string"}, "description": "New phone numbers."},
                },
                "required": ["resource_name"],
            },
        ),
        Tool(
            name="people.delete_contact",
            description="Delete a contact.",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_name": {"type": "string", "description": "Contact resource name to delete."},
                },
                "required": ["resource_name"],
            },
        ),
        Tool(
            name="people.batch_create_contacts",
            description="Batch create multiple contacts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "contacts": {"type": "array", "items": {"type": "object"}, "description": "Array of contact objects."},
                },
                "required": ["contacts"],
            },
        ),
        Tool(
            name="people.create_contact_group",
            description="Create a new contact group.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Group name."},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="people.add_contact_to_group",
            description="Add a contact to a group.",
            inputSchema={
                "type": "object",
                "properties": {
                    "group_resource_name": {"type": "string", "description": "Group resource name."},
                    "contact_resource_name": {"type": "string", "description": "Contact resource name."},
                },
                "required": ["group_resource_name", "contact_resource_name"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "people.list_contacts": svc.list_contacts,
        "people.get_contact": svc.get_contact,
        "people.search_contacts": svc.search_contacts,
        "people.create_contact": svc.create_contact,
        "people.update_contact": svc.update_contact,
        "people.delete_contact": svc.delete_contact,
        "people.batch_create_contacts": svc.batch_create_contacts,
        "people.create_contact_group": svc.create_contact_group,
        "people.add_contact_to_group": svc.add_contact_to_group,
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
