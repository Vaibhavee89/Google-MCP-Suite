# Dev Notes

## Configuration
- Default config path: `~/.google-mcp/config.yaml`.
- Override with `GOOGLE_MCP_CONFIG` environment variable.
- Service scopes are merged with `google.default_scopes`.

## Auth Modes
- `oauth`: user consent flow with refresh tokens saved to token store.
- `service_account`: supports domain-wide delegation via `subject`.

## Tool Conventions
- Search tools accept `query`, `limit`, `page_token` and return `{items, next_page_token}`.
- Read tools accept an `id` and return full resource payload.
- Destructive tools require confirmation flags (e.g., `confirm`).
