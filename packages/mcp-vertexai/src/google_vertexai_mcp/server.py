from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_vertexai_mcp.service import VertexAIService

app = Server("google-vertexai-mcp")


@lru_cache(maxsize=1)
def _svc() -> VertexAIService:
    """One service per process: config is read once and Google clients are reused."""
    return VertexAIService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="vertexai_list_models",
            description="List Vertex AI models.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 50},
                },
            },
        ),
        Tool(
            name="vertexai_get_model",
            description="Get Vertex AI model details.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_id": {"type": "string", "description": "Model ID."},
                },
                "required": ["model_id"],
            },
        ),
        Tool(
            name="vertexai_list_endpoints",
            description="List Vertex AI endpoints.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 50},
                },
            },
        ),
        Tool(
            name="vertexai_get_endpoint",
            description="Get Vertex AI endpoint details.",
            inputSchema={
                "type": "object",
                "properties": {
                    "endpoint_id": {"type": "string", "description": "Endpoint ID."},
                },
                "required": ["endpoint_id"],
            },
        ),
        Tool(
            name="vertexai_list_datasets",
            description="List Vertex AI datasets.",
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
        "vertexai_list_models": svc.list_models,
        "vertexai_get_model": svc.get_model,
        "vertexai_list_endpoints": svc.list_endpoints,
        "vertexai_get_endpoint": svc.get_endpoint,
        "vertexai_list_datasets": svc.list_datasets,
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
