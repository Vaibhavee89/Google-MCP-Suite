from __future__ import annotations

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from google_pubsub_mcp.service import PubSubService

app = Server("google-pubsub-mcp")


def _svc() -> PubSubService:
    return PubSubService.from_config()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="pubsub.list_topics",
            description="List Pub/Sub topics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 50},
                },
            },
        ),
        Tool(
            name="pubsub.get_topic",
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
            name="pubsub.list_subscriptions",
            description="List Pub/Sub subscriptions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 50},
                },
            },
        ),
        Tool(
            name="pubsub.get_subscription",
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
        "pubsub.list_topics": svc.list_topics,
        "pubsub.get_topic": svc.get_topic,
        "pubsub.list_subscriptions": svc.list_subscriptions,
        "pubsub.get_subscription": svc.get_subscription,
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
