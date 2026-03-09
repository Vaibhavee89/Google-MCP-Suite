#!/usr/bin/env python3
"""Run the Google Calendar MCP HTTP server for testing with MCP clients."""

import sys
import uvicorn

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    host = sys.argv[2] if len(sys.argv) > 2 else "0.0.0.0"

    print(f"Starting Google Calendar MCP HTTP server on {host}:{port}")
    print(f"MCP endpoint: http://{host}:{port}/mcp")
    print(f"Health check: http://{host}:{port}/health")
    print("\nPress CTRL+C to stop the server\n")

    uvicorn.run(
        "google_calendar_mcp.http_server:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
