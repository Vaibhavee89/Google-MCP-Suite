from __future__ import annotations

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_sheets_mcp.service import SheetsService

app = Server("google-sheets-mcp")


def _svc() -> SheetsService:
    return SheetsService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="sheets.read_range",
            description="Read values from a Sheets range (A1 notation).",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID."},
                    "range_a1": {"type": "string", "description": "A1 range notation (e.g. Sheet1!A1:D10)."},
                    "major_dimension": {"type": "string", "description": "ROWS or COLUMNS.", "default": "ROWS"},
                    "value_render_option": {"type": "string", "description": "FORMATTED_VALUE, UNFORMATTED_VALUE, or FORMULA.", "default": "FORMATTED_VALUE"},
                },
                "required": ["spreadsheet_id", "range_a1"],
            },
        ),
        Tool(
            name="sheets.get_metadata",
            description="Get spreadsheet metadata (title, sheets, etc.).",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID."},
                },
                "required": ["spreadsheet_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "sheets.read_range": svc.read_range,
        "sheets.get_metadata": svc.get_metadata,
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
