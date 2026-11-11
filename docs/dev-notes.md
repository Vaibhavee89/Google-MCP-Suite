# Dev Notes

## Configuration
- Default config path: `~/.google-mcp/config.yaml`.
- Override with `GOOGLE_MCP_CONFIG` environment variable.
- Service scopes are merged with `google.default_scopes`.
- `google.allowed_scopes` (optional) is a hard ceiling; requests outside it fail with `scope_not_allowed`.

## Write safety
Destructive/outward-facing tools (`gmail.send_email`, `gmail.reply_to_message`,
`gmail.delete_message`, `drive.delete_file`, `drive.share_file`) need two things:
1. The server operator sets `GOOGLE_MCP_ALLOW_WRITES=1` in the MCP server's environment
   (e.g. `claude mcp add -e GOOGLE_MCP_ALLOW_WRITES=1 google-gmail -- ...`). Off by default;
   otherwise calls fail with `writes_disabled`.
2. The call passes `confirm=true`.

The agent controls only (2), so (1) is what actually stops an agent from acting alone.

## Auth Modes
- `oauth`: user consent flow with refresh tokens saved to token store.
- `service_account`: supports domain-wide delegation via `subject`.

## Tool Conventions
- Search tools accept `query`, `limit`, `page_token` and return `{items, next_page_token}`.
- Read tools accept an `id` and return full resource payload.
- Destructive tools require confirmation flags (e.g., `confirm`).
