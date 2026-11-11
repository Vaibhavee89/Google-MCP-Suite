from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_pubsub_mcp.service import PubSubService

app = Server("google-pubsub-mcp")


@lru_cache(maxsize=1)
def _svc() -> PubSubService:
    """One service per process: config is read once and Google clients are reused."""
    return PubSubService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="pubsub_list_topics",
            description="List Pub/Sub topics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 50},
                },
            },
        ),
        Tool(
            name="pubsub_get_topic",
            description="Get Pub/Sub topic details.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic_name": {"type": "string", "description": "Topic name."},
                },
                "required": ["topic_name"],
            },
        ),
        Tool(
            name="pubsub_list_subscriptions",
            description="List Pub/Sub subscriptions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 50},
                },
            },
        ),
        Tool(
            name="pubsub_get_subscription",
            description="Get Pub/Sub subscription details.",
            inputSchema={
                "type": "object",
                "properties": {
                    "subscription_name": {"type": "string", "description": "Subscription name."},
                },
                "required": ["subscription_name"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    svc = _svc()
    handlers = {
        "pubsub_list_topics": svc.list_topics,
        "pubsub_get_topic": svc.get_topic,
        "pubsub_list_subscriptions": svc.list_subscriptions,
        "pubsub_get_subscription": svc.get_subscription,
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
