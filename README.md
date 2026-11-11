# Google MCP Suite

Eighteen [Model Context Protocol](https://modelcontextprotocol.io) servers for Google Workspace and Google Cloud, built on a shared core for auth, retries, pagination, errors and write safety. Each server is a small stdio process you register with Claude Code, Claude Desktop or any MCP client.

**Write tools are locked down by default.** Anything that sends, deletes, shares or edits needs `confirm=true`, destructive tools additionally need an operator switch, and a single env var turns the whole suite read-only. See [Safety](#safety).

## Servers

| Server | Package | Module | Tools |
| --- | --- | --- | ---: |
| Gmail | `packages/mcp-gmail` | `google_gmail_mcp` | 12 |
| Google Drive | `packages/mcp-google-drive` | `google_drive_mcp` | 13 |
| Calendar | `packages/mcp-calendar` | `google_calendar_mcp` | 10 |
| Sheets | `packages/mcp-sheets` | `google_sheets_mcp` | 10 |
| Docs | `packages/mcp-docs` | `google_docs_mcp` | 9 |
| Slides | `packages/mcp-slides` | `google_slides_mcp` | 9 |
| Forms | `packages/mcp-forms` | `google_forms_mcp` | 10 |
| Tasks | `packages/mcp-tasks` | `google_tasks_mcp` | 10 |
| People (Contacts) | `packages/mcp-people` | `google_people_mcp` | 9 |
| Meet | `packages/mcp-meet` | `google_meet_mcp` | 2 |
| Admin SDK (Directory) | `packages/mcp-admin-sdk` | `google_admin_sdk_mcp` | 2 |
| Chat | `packages/mcp-chat` | `google_chat_mcp` | 2 |
| Cloud Storage | `packages/mcp-gcs` | `google_gcs_mcp` | 3 |
| BigQuery | `packages/mcp-bigquery` | `google_bigquery_mcp` | 5 |
| Cloud Logging | `packages/mcp-cloudlogging` | `google_cloudlogging_mcp` | 3 |
| Cloud Run | `packages/mcp-cloudrun` | `google_cloudrun_mcp` | 3 |
| Pub/Sub | `packages/mcp-pubsub` | `google_pubsub_mcp` | 4 |
| Vertex AI | `packages/mcp-vertexai` | `google_vertexai_mcp` | 5 |
| | | **Total** | **121** |

Shared code lives in `packages/core` (`google_mcp_core`). Tool names are `<service>_<tool>` (letters, digits and underscores only, so every MCP client accepts them), e.g. `gmail_send_email`.

<details>
<summary>Tools by server</summary>

- **Gmail** (`gmail_`): search_messages, read_message, send_email, create_draft, reply_to_message, modify_labels, trash_message, delete_message, mark_as_read, mark_as_unread, list_labels, create_label
- **Drive** (`drive_`): search_files, get_metadata, read_text, download, list_children, get_permissions, create_folder, upload_file, move_file, copy_file, delete_file, share_file, update_file_metadata
- **Calendar** (`calendar_`): search_events, get_event, create_event, update_event, delete_event, list_calendars, create_calendar, add_attendees, quick_add_event, check_freebusy
- **Sheets** (`sheets_`): read_range, get_metadata, update_values, append_values, batch_update, create_spreadsheet, add_sheet, delete_sheet, clear_values, format_cells
- **Docs** (`docs_`): get_document, export_text, create_document, insert_text, delete_text, replace_text, append_text, format_text, insert_image
- **Slides** (`slides_`): get_presentation, get_slide_content, list_presentations, extract_text, create_slide, add_text_to_slide, update_text, delete_slide, create_presentation
- **Forms** (`forms_`): get_form, list_responses, get_response, create_form, add_text_question, add_multiple_choice_question, add_checkbox_question, update_form_info, delete_item, update_settings
- **Tasks** (`tasks_`): list_task_lists, list_tasks, get_task, create_task, update_task, delete_task, complete_task, create_task_list, delete_task_list, move_task
- **People** (`people_`): list_contacts, get_contact, search_contacts, create_contact, update_contact, delete_contact, batch_create_contacts, create_contact_group, add_contact_to_group
- **Meet** (`meet_`): list_activities, get_activity
- **Admin SDK** (`admin_`): list_users, get_user
- **Chat** (`chat_`): list_spaces, search_messages
- **Cloud Storage** (`gcs_`): list_objects, get_object_metadata, download_object
- **BigQuery** (`bigquery_`): list_datasets, list_tables, get_table_schema, query, list_jobs
- **Cloud Logging** (`cloudlogging_`): list_logs, query_logs, get_log_metrics
- **Cloud Run** (`cloudrun_`): list_services, get_service, list_revisions
- **Pub/Sub** (`pubsub_`): list_topics, get_topic, list_subscriptions, get_subscription
- **Vertex AI** (`vertexai_`): list_models, get_model, list_endpoints, get_endpoint, list_datasets

</details>

## Quick start

Requires Python 3.10+ and a Google Cloud project.

**1. Create OAuth credentials.** In the [Cloud Console](https://console.cloud.google.com/), enable the APIs you want (Gmail, Drive, Calendar, ...), then create an *OAuth client ID* of type **Desktop app**.

**2. Write your config.**

```bash
mkdir -p ~/.google-mcp
cp docs/config.example.yaml ~/.google-mcp/config.yaml   # then fill in client_id / client_secret
```

Use `GOOGLE_MCP_CONFIG=/path/to/config.yaml` to point a server at a different file. Keep `config.yaml` and `~/.google-mcp/tokens.json` out of version control.

**3. Install.** The servers use the `mcp` 1.x API, so keep it below 2.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e packages/core "mcp<2"
pip install -e packages/mcp-gmail -e packages/mcp-google-drive -e packages/mcp-calendar   # the servers you want
```

**4. Authorize once.** `python authenticate.py` opens a browser for OAuth consent and stores a token in `~/.google-mcp/tokens.json`.

**5. Check a server starts.**

```bash
python -m google_gmail_mcp.server     # speaks MCP over stdio; Ctrl-C to quit
```

## Connect to Claude

Every server runs over stdio, either as `python -m <module>.server` or through the console script `pip install` puts next to your Python (`google-gmail-mcp`, `google-drive-mcp`, ... named after the server). Point `command` at the Python inside the virtualenv you installed into (`.venv/bin/python`) so the right packages are found. Replace `/ABS/PATH` below.

### Claude Code

```bash
claude mcp add google-gmail  --env GOOGLE_MCP_READ_ONLY=1 -- /ABS/PATH/.venv/bin/python -m google_gmail_mcp.server
claude mcp add google-drive  --env GOOGLE_MCP_READ_ONLY=1 -- /ABS/PATH/.venv/bin/python -m google_drive_mcp.server
claude mcp add google-calendar --env GOOGLE_MCP_READ_ONLY=1 -- /ABS/PATH/.venv/bin/python -m google_calendar_mcp.server
```

Or create a project-level `.mcp.json` (it holds machine-specific paths, so keep it out of version control):

```json
{
  "mcpServers": {
    "google-gmail": {
      "command": "/ABS/PATH/.venv/bin/python",
      "args": ["-m", "google_gmail_mcp.server"],
      "env": { "GOOGLE_MCP_READ_ONLY": "1" }
    },
    "google-drive": {
      "command": "/ABS/PATH/.venv/bin/python",
      "args": ["-m", "google_drive_mcp.server"],
      "env": { "GOOGLE_MCP_READ_ONLY": "1" }
    }
  }
}
```

### Claude Desktop

Add the same `mcpServers` block to `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`), then restart Claude Desktop:

```json
{
  "mcpServers": {
    "google-gmail": {
      "command": "/ABS/PATH/.venv/bin/python",
      "args": ["-m", "google_gmail_mcp.server"],
      "env": { "GOOGLE_MCP_READ_ONLY": "1" }
    }
  }
}
```

The examples start read-only. To allow writes, drop `GOOGLE_MCP_READ_ONLY`; to allow delete/send/share as well, add `"GOOGLE_MCP_ALLOW_WRITES": "1"`. Registering one entry per server keeps each server's tools and scopes separate; add only the ones you need.

> Avoid blanket auto-approval (`autoApprove`) for write tools. The `confirm` flag is only a speed bump if the client approves every call automatically.

## Safety

All write tools go through `google_mcp_core.safety`:

| Control | Effect |
| --- | --- |
| `GOOGLE_MCP_READ_ONLY=1` | Every write tool fails with `read_only`, regardless of the other settings. |
| `confirm=true` argument | Required by every gated write; otherwise `confirmation_required`. |
| `GOOGLE_MCP_ALLOW_WRITES=1` | Also required for destructive or outbound tools (send, reply, delete, trash, share, move, clear, add attendees...); otherwise `writes_disabled`. |
| `google.allowed_scopes` in `config.yaml` | Hard ceiling on OAuth scopes; anything outside it is rejected (`scope_not_allowed`). |

The agent only controls `confirm`. The two environment variables are set by whoever starts the server, which is what stops an agent from acting alone. Full list of gated tools: [`docs/dev-notes.md`](docs/dev-notes.md#write-safety).

## Behaviour notes

- **Errors are MCP errors.** A failed call returns a tool result with `isError: true` and the text `<code>: <message>` (e.g. `confirmation_required: ...`, `read_only: ...`, `google_http_404: ...`), not a successful result containing "Error: ...".
- **One service per server process.** Config is read once, on the first call, and Google API clients are reused. Restart the server after editing `config.yaml`. The safety environment variables are re-read on every call.
- **Token file is owner-only.** `~/.google-mcp/tokens.json` is written with mode `0600` (atomically, so it is never briefly readable by others). An older token file with looser permissions is tightened the next time the token is saved, e.g. on refresh.

## Development

```bash
pip install -e packages/core "mcp<2" pytest ruff $(for d in packages/mcp-*; do echo "-e $d"; done)
ruff check .
python -m pytest packages/core/tests -q
```

Tests use mocked Google clients, so they need no credentials or network. CI (`.github/workflows/ci.yml`) runs ruff and pytest on Python 3.10, 3.11 and 3.12. Installing every server also pulls in the `google-cloud-*` libraries the six Google Cloud servers need; without them their tests are skipped.

## More documentation

- [`docs/config.example.yaml`](docs/config.example.yaml): configuration reference.
- [`docs/service-matrix.md`](docs/service-matrix.md): auth modes, client libraries and rate limits per service.
- [`docs/claude-code-setup.md`](docs/claude-code-setup.md), [`CLAUDE_CODE_SETUP.md`](CLAUDE_CODE_SETUP.md): longer setup walkthroughs, including the HTTP-transport scripts (`start_all_mcps.sh`). Those older guides recommend auto-approving every tool; prefer the defaults above.
- [`README_DISTRIBUTION.md`](README_DISTRIBUTION.md), [`DISTRIBUTION_NOTES.md`](DISTRIBUTION_NOTES.md): packaging a distributable bundle.
- [`docs/archive/`](docs/archive/): historical implementation status reports (their tool counts are out of date).
