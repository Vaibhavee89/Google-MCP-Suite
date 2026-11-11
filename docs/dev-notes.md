# Dev Notes

## Configuration
- Default config path: `~/.google-mcp/config.yaml`.
- Override with `GOOGLE_MCP_CONFIG` environment variable.
- Service scopes are merged with `google.default_scopes`.
- `google.allowed_scopes` (optional) is a hard ceiling; requests outside it fail with `scope_not_allowed`.

## Write safety
Every write tool goes through `google_mcp_core.safety`:

- **Read-only mode.** Set `GOOGLE_MCP_READ_ONLY=1` in the MCP server's environment and every
  write tool (gated or not) fails with `read_only`, regardless of `confirm` or
  `GOOGLE_MCP_ALLOW_WRITES`. It covers all of Gmail, Drive, Calendar, Sheets, Docs, Forms,
  Tasks, People and Slides writes.
- **`confirm=true`.** Writes in Sheets, Docs, Forms, Tasks and People, plus Drive `create_folder`,
  need `confirm=true`, otherwise `confirmation_required`.
- **Destructive / outbound tools** need `confirm=true` *and* the operator switch
  `GOOGLE_MCP_ALLOW_WRITES=1` (e.g. `claude mcp add -e GOOGLE_MCP_ALLOW_WRITES=1 google-gmail -- ...`);
  otherwise `writes_disabled`. These are: `gmail_send_email`, `gmail_reply_to_message`,
  `gmail_trash_message`, `gmail_delete_message`; `drive_delete_file`, `drive_share_file`,
  `drive_move_file`; `calendar_delete_event`, `calendar_add_attendees`; `sheets_batch_update`,
  `sheets_delete_sheet`, `sheets_clear_values`; `docs_delete_text`; `forms_delete_item`;
  `tasks_delete_task`, `tasks_delete_task_list`; `people_delete_contact`.
- Writes with no `confirm` parameter (Gmail drafts/labels, Drive upload/copy/metadata, Calendar
  create/update/quick-add/create-calendar, Slides) only honour read-only mode.

The agent controls only `confirm`; the environment switches are what stop it acting alone.
`google.allowed_scopes` (see above) is enforced in `AuthManager.get_credentials`, the single
place credentials are built.

## Auth Modes
- `oauth`: user consent flow with refresh tokens saved to token store.
- `service_account`: supports domain-wide delegation via `subject`.

## Tool Conventions
- Search tools accept `query`, `limit`, `page_token` and return `{items, next_page_token}`.
- Read tools accept an `id` and return full resource payload.
- Destructive tools require confirmation flags (e.g., `confirm`).
