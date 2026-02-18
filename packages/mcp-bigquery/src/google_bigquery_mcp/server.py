from __future__ import annotations

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_bigquery_mcp.service import BigQueryService

app = Server("google-bigquery-mcp")


def _svc() -> BigQueryService:
    return BigQueryService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="bigquery.list_datasets",
            description="List BigQuery datasets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 50},
                },
            },
        ),
        Tool(
            name="bigquery.list_tables",
            description="List tables in a dataset.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID."},
                    "limit": {"type": "integer", "description": "Max results.", "default": 100},
                },
                "required": ["dataset_id"],
            },
        ),
        Tool(
            name="bigquery.get_table_schema",
            description="Get table schema and metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID."},
                    "table_id": {"type": "string", "description": "Table ID."},
                },
                "required": ["dataset_id", "table_id"],
            },
        ),
        Tool(
            name="bigquery.query",
            description="Execute a BigQuery SQL query (read-only).",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "SQL query."},
                    "limit": {"type": "integer", "description": "Max rows to return.", "default": 100},
                },
                "required": ["sql"],
            },
        ),
        Tool(
            name="bigquery.list_jobs",
            description="List recent BigQuery jobs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 50},
                },
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "bigquery.list_datasets": svc.list_datasets,
        "bigquery.list_tables": svc.list_tables,
        "bigquery.get_table_schema": svc.get_table_schema,
        "bigquery.query": svc.query,
        "bigquery.list_jobs": svc.list_jobs,
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
