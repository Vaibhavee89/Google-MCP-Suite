from __future__ import annotations

import contextlib

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

from google_calendar_mcp.server import app as mcp_app


session_manager = StreamableHTTPSessionManager(
    mcp_app,
    stateless=False,
    json_response=False,
)


@contextlib.asynccontextmanager
async def lifespan(_: Starlette):
    async with session_manager.run():
        yield


async def handle_mcp(scope, receive, send):
    await session_manager.handle_request(scope, receive, send)


async def healthcheck(_request):
    return PlainTextResponse("ok")


app = Starlette(
    routes=[
        Route("/mcp", handle_mcp, methods=["GET", "POST", "DELETE"]),
        Route("/health", healthcheck, methods=["GET"]),
    ],
    lifespan=lifespan,
)
