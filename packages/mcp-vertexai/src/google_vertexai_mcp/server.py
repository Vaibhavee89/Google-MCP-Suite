from __future__ import annotations

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_vertexai_mcp.service import VertexAIService

app = Server("google-vertexai-mcp")


def _svc() -> VertexAIService:
    return VertexAIService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="vertexai.list_models",
            description="List Vertex AI models.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 50},
                },
            },
        ),
        Tool(
            name="vertexai.get_model",
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
            name="vertexai.list_endpoints",
            description="List Vertex AI endpoints.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 50},
                },
            },
        ),
        Tool(
            name="vertexai.get_endpoint",
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
            name="vertexai.list_datasets",
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
        "vertexai.list_models": svc.list_models,
        "vertexai.get_model": svc.get_model,
        "vertexai.list_endpoints": svc.list_endpoints,
        "vertexai.get_endpoint": svc.get_endpoint,
        "vertexai.list_datasets": svc.list_datasets,
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
