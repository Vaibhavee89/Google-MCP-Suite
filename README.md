# Google MCP Suite (Python)

Monorepo of Model Context Protocol (MCP) servers for Google services with a shared core for auth, pagination, errors, and safety.

## Packages
- `packages/core`: shared framework (auth, client factory, pagination, errors, logging, safety).
- `packages/mcp-google-drive`: Drive MCP server (golden path).
- `packages/mcp-gmail`: Gmail MCP server (search/read).
- `packages/mcp-calendar`: Calendar MCP server (search/read).
- `packages/mcp-sheets`: Sheets MCP server (read-only).
- `packages/mcp-docs`: Docs MCP server (read/export).
- `packages/mcp-gcs`: GCS MCP server (read/list/download).
- `packages/mcp-meet`: Meet MCP server (Admin Reports activities).
- `packages/mcp-admin-sdk`: Admin SDK MCP server (Directory read).
- `packages/mcp-chat`: Chat MCP server (spaces/messages).

## Quick Start
1. Create OAuth credentials in Google Cloud Console (Desktop or Web app).
2. Copy `docs/config.example.yaml` to `~/.google-mcp/config.yaml` and fill values.
3. Install a package locally, e.g.:
   ```bash
   pip install -e packages/core
   pip install -e packages/mcp-google-drive
   ```
4. Run a server (example):
   ```bash
   python -m google_drive_mcp.server
   ```

## Documentation
- `docs/service-matrix.md`: service scope, auth, and rate-limit matrix.
- `docs/config.example.yaml`: configuration reference.
# Google-MCP-Suite
