from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_sheets_mcp.service import SheetsService

app = Server("google-sheets-mcp")


@lru_cache(maxsize=1)
def _svc() -> SheetsService:
    """One service per process: config is read once and Google clients are reused."""
    return SheetsService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="sheets_read_range",
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
            name="sheets_get_metadata",
            description="Get spreadsheet metadata (title, sheets, etc.).",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID."},
                },
                "required": ["spreadsheet_id"],
            },
        ),
        Tool(
            name="sheets_update_values",
            description="Update cell values in a spreadsheet (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID."},
                    "range_a1": {"type": "string", "description": "A1 range notation."},
                    "values": {"type": "array", "items": {"type": "array"}, "description": "2D array of values."},
                    "value_input_option": {"type": "string", "description": "USER_ENTERED or RAW.", "default": "USER_ENTERED"},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["spreadsheet_id", "range_a1", "values", "confirm"],
            },
        ),
        Tool(
            name="sheets_append_values",
            description="Append rows to a spreadsheet (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID."},
                    "range_a1": {"type": "string", "description": "A1 range notation."},
                    "values": {"type": "array", "items": {"type": "array"}, "description": "2D array of values."},
                    "value_input_option": {"type": "string", "description": "USER_ENTERED or RAW.", "default": "USER_ENTERED"},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["spreadsheet_id", "range_a1", "values", "confirm"],
            },
        ),
        Tool(
            name="sheets_batch_update",
            description="Execute batch update operations (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID."},
                    "requests": {"type": "array", "items": {"type": "object"}, "description": "Array of update requests."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["spreadsheet_id", "requests", "confirm"],
            },
        ),
        Tool(
            name="sheets_create_spreadsheet",
            description="Create a new spreadsheet (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Spreadsheet title."},
                    "sheets": {"type": "array", "items": {"type": "object"}, "description": "Array of sheet definitions."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["title", "confirm"],
            },
        ),
        Tool(
            name="sheets_add_sheet",
            description="Add a new sheet to a spreadsheet (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID."},
                    "title": {"type": "string", "description": "Sheet title."},
                    "row_count": {"type": "integer", "description": "Number of rows.", "default": 1000},
                    "column_count": {"type": "integer", "description": "Number of columns.", "default": 26},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["spreadsheet_id", "title", "confirm"],
            },
        ),
        Tool(
            name="sheets_delete_sheet",
            description="Delete a sheet from a spreadsheet (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID."},
                    "sheet_id": {"type": "integer", "description": "Sheet ID to delete."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["spreadsheet_id", "sheet_id", "confirm"],
            },
        ),
        Tool(
            name="sheets_clear_values",
            description="Clear cell values in a range (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID."},
                    "range_a1": {"type": "string", "description": "A1 range notation."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["spreadsheet_id", "range_a1", "confirm"],
            },
        ),
        Tool(
            name="sheets_format_cells",
            description="Format cells in a range (requires confirm=true).",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID."},
                    "sheet_id": {"type": "integer", "description": "Sheet ID."},
                    "start_row": {"type": "integer", "description": "Start row index."},
                    "end_row": {"type": "integer", "description": "End row index."},
                    "start_col": {"type": "integer", "description": "Start column index."},
                    "end_col": {"type": "integer", "description": "End column index."},
                    "format_data": {"type": "object", "description": "Format specification."},
                    "confirm": {"type": "boolean", "description": "Must be true to execute.", "default": False},
                },
                "required": ["spreadsheet_id", "sheet_id", "start_row", "end_row", "start_col", "end_col", "format_data", "confirm"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "sheets_read_range": svc.read_range,
        "sheets_get_metadata": svc.get_metadata,
        "sheets_update_values": svc.update_values,
        "sheets_append_values": svc.append_values,
        "sheets_batch_update": svc.batch_update,
        "sheets_create_spreadsheet": svc.create_spreadsheet,
        "sheets_add_sheet": svc.add_sheet,
        "sheets_delete_sheet": svc.delete_sheet,
        "sheets_clear_values": svc.clear_values,
        "sheets_format_cells": svc.format_cells,
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
