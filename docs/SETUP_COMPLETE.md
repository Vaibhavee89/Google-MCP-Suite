# Google MCP Suite - Complete Setup Guide

## ✅ Implementation Status

All Google MCP services have been successfully implemented:

### Tier 1 (High Value, Common)
- ✅ Google Drive
- ✅ Gmail
- ✅ Google Calendar
- ✅ Google Sheets
- ✅ Google Docs
- ✅ Google Meet
- ✅ Google Cloud Storage (GCS)
- ✅ **Google Slides/Presentations** (NEW)

### Tier 2 (Workflows & Automation)
- ✅ Google Chat
- ✅ Admin SDK
- ✅ **Google Forms** (NEW)
- ✅ **Google Tasks** (NEW)
- ✅ **People API/Contacts** (NEW)

### Tier 3 (GCP Heavy / Specialized)
- ✅ **BigQuery** (NEW)
- ✅ **Cloud Logging** (NEW)
- ✅ **Pub/Sub** (NEW)
- ✅ **Cloud Run** (NEW)
- ✅ **Vertex AI** (NEW)

---

## 📦 Installation

All packages have been installed using the custom installation script that works around Python 3.13 editable install issues.

```bash
cd /Users/vaibhavee/project/MCP_Suite
./install_all.sh
```

---

## 🔐 OAuth Re-Authorization Required

Since we've added 10 new services with additional OAuth scopes, you need to re-authorize to get a token with all required permissions.

### Step 1: Delete Existing Token

```bash
rm ~/.google-mcp/tokens.json
```

### Step 2: Trigger OAuth Flow

Run any MCP server to trigger the OAuth flow with all scopes:

```bash
cd /Users/vaibhavee/project/MCP_Suite
.venv/bin/python -m google_drive_mcp.server
```

This will:
1. Open your browser for Google OAuth consent
2. Request all scopes from your `config.yaml`
3. Save the token to `~/.google-mcp/tokens.json`

**Important:** Make sure you grant all requested permissions!

---

## 📝 Register MCPs with Claude Code

Use the following commands to register all MCPs with Claude Code:

### Tier 1 Services

```bash
# Google Drive
claude mcp add google-drive -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_drive_mcp.server

# Gmail
claude mcp add google-gmail -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_gmail_mcp.server

# Google Calendar
claude mcp add google-calendar -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_calendar_mcp.server

# Google Sheets
claude mcp add google-sheets -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_sheets_mcp.server

# Google Docs
claude mcp add google-docs -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_docs_mcp.server

# Google Slides (NEW)
claude mcp add google-slides -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_slides_mcp.server

# Google Meet
claude mcp add google-meet -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_meet_mcp.server

# Google Cloud Storage
claude mcp add google-gcs -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_gcs_mcp.server
```

### Tier 2 Services

```bash
# Google Chat
claude mcp add google-chat -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_chat_mcp.server

# Admin SDK
claude mcp add google-admin-sdk -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_admin_sdk_mcp.server

# Google Forms (NEW)
claude mcp add google-forms -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_forms_mcp.server

# Google Tasks (NEW)
claude mcp add google-tasks -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_tasks_mcp.server

# People API/Contacts (NEW)
claude mcp add google-people -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_people_mcp.server
```

### Tier 3 Services (GCP)

**Note:** For GCP services, you may need to set the `project_id` environment variable or configure it in your service initialization.

```bash
# BigQuery (NEW)
claude mcp add google-bigquery -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_bigquery_mcp.server

# Cloud Logging (NEW)
claude mcp add google-cloudlogging -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_cloudlogging_mcp.server

# Pub/Sub (NEW)
claude mcp add google-pubsub -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_pubsub_mcp.server

# Cloud Run (NEW)
claude mcp add google-cloudrun -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_cloudrun_mcp.server

# Vertex AI (NEW)
claude mcp add google-vertexai -- /Users/vaibhavee/project/MCP_Suite/.venv/bin/python -m google_vertexai_mcp.server
```

---

## 🔍 Verify MCP Registration

List all registered MCPs:

```bash
claude mcp list
```

Test a specific MCP:

```bash
claude mcp test google-slides
```

---

## 📋 All OAuth Scopes Required

Your `~/.google-mcp/config.yaml` now includes these scopes:

```yaml
services:
  drive:
    scopes:
      - "https://www.googleapis.com/auth/drive.readonly"
  gmail:
    scopes:
      - "https://www.googleapis.com/auth/gmail.readonly"
  calendar:
    scopes:
      - "https://www.googleapis.com/auth/calendar.readonly"
  sheets:
    scopes:
      - "https://www.googleapis.com/auth/spreadsheets.readonly"
  docs:
    scopes:
      - "https://www.googleapis.com/auth/documents.readonly"
  slides:
    scopes:
      - "https://www.googleapis.com/auth/presentations.readonly"
  forms:
    scopes:
      - "https://www.googleapis.com/auth/forms.responses.readonly"
  tasks:
    scopes:
      - "https://www.googleapis.com/auth/tasks.readonly"
  people:
    scopes:
      - "https://www.googleapis.com/auth/contacts.readonly"
  gcs:
    scopes:
      - "https://www.googleapis.com/auth/devstorage.read_only"
  meet:
    scopes:
      - "https://www.googleapis.com/auth/admin.reports.audit.readonly"
  admin_sdk:
    scopes:
      - "https://www.googleapis.com/auth/admin.directory.user.readonly"
  chat:
    scopes:
      - "https://www.googleapis.com/auth/chat.messages.readonly"
  bigquery:
    scopes:
      - "https://www.googleapis.com/auth/bigquery.readonly"
  cloudlogging:
    scopes:
      - "https://www.googleapis.com/auth/logging.read"
  pubsub:
    scopes:
      - "https://www.googleapis.com/auth/pubsub"
  cloudrun:
    scopes:
      - "https://www.googleapis.com/auth/cloud-platform.read-only"
  vertexai:
    scopes:
      - "https://www.googleapis.com/auth/cloud-platform"
```

---

## 🧪 Testing Individual MCPs

Test each MCP by running its server directly:

```bash
# Test Google Slides
.venv/bin/python -m google_slides_mcp.server

# Test Google Forms
.venv/bin/python -m google_forms_mcp.server

# Test Google Tasks
.venv/bin/python -m google_tasks_mcp.server

# Test People API
.venv/bin/python -m google_people_mcp.server

# Test BigQuery
.venv/bin/python -m google_bigquery_mcp.server

# Test Cloud Logging
.venv/bin/python -m google_cloudlogging_mcp.server

# Test Pub/Sub
.venv/bin/python -m google_pubsub_mcp.server

# Test Cloud Run
.venv/bin/python -m google_cloudrun_mcp.server

# Test Vertex AI
.venv/bin/python -m google_vertexai_mcp.server
```

Each server will start and wait for MCP protocol messages via stdin/stdout.

---

## 🎯 Available Tools by Service

### Google Slides
- `slides.get_presentation` - Get presentation metadata
- `slides.get_slide` - Get specific slide content
- `slides.list_presentations` - List all presentations
- `slides.extract_text` - Extract all text from a presentation

### Google Forms
- `forms.get_form` - Get form metadata and structure
- `forms.list_responses` - List form responses
- `forms.get_response` - Get a specific form response

### Google Tasks
- `tasks.list_task_lists` - List all task lists
- `tasks.list_tasks` - List tasks in a task list
- `tasks.get_task` - Get a specific task

### People API/Contacts
- `people.list_contacts` - List contacts
- `people.get_contact` - Get detailed contact information
- `people.search_contacts` - Search contacts by name, email, or phone

### BigQuery
- `bigquery.list_datasets` - List BigQuery datasets
- `bigquery.list_tables` - List tables in a dataset
- `bigquery.get_table_schema` - Get table schema and metadata
- `bigquery.query` - Execute a SQL query (read-only)
- `bigquery.list_jobs` - List recent BigQuery jobs

### Cloud Logging
- `cloudlogging.list_logs` - List recent log entries
- `cloudlogging.query_logs` - Query logs with a filter expression
- `cloudlogging.get_log_metrics` - List log-based metrics

### Pub/Sub
- `pubsub.list_topics` - List Pub/Sub topics
- `pubsub.get_topic` - Get topic details
- `pubsub.list_subscriptions` - List Pub/Sub subscriptions
- `pubsub.get_subscription` - Get subscription details

### Cloud Run
- `cloudrun.list_services` - List Cloud Run services
- `cloudrun.get_service` - Get service details
- `cloudrun.list_revisions` - List service revisions

### Vertex AI
- `vertexai.list_models` - List Vertex AI models
- `vertexai.get_model` - Get model details
- `vertexai.list_endpoints` - List Vertex AI endpoints
- `vertexai.get_endpoint` - Get endpoint details
- `vertexai.list_datasets` - List Vertex AI datasets

---

## 🐛 Troubleshooting

### "Insufficient Permission" Error

Delete your token and re-authorize:
```bash
rm ~/.google-mcp/tokens.json
.venv/bin/python -m google_drive_mcp.server
```

### "Cannot import module" Error

Verify the installation:
```bash
./install_all.sh
```

### GCP Services Not Working

For GCP services (BigQuery, Cloud Logging, Pub/Sub, Cloud Run, Vertex AI), you need:
1. A GCP project with the respective APIs enabled
2. The project ID configured (either via environment variable or in service initialization)
3. Appropriate IAM permissions

### MCP Not Responding in Claude Code

1. Check MCP is registered: `claude mcp list`
2. Test MCP directly: `claude mcp test <mcp-name>`
3. Check logs in Claude Code for error messages

---

## 📚 Next Steps

1. **Delete existing token:** `rm ~/.google-mcp/tokens.json`
2. **Re-authorize with all scopes:** Run any MCP server to trigger OAuth
3. **Register all MCPs:** Use the commands above
4. **Test in Claude Code:** Try asking Claude to list your Google Slides or Forms

---

## 🎉 Summary

You now have a complete Google MCP Suite with **19 services** covering:
- Core Google Workspace services (Drive, Gmail, Calendar, Sheets, Docs, Slides)
- Collaboration tools (Meet, Chat, Forms, Tasks, Contacts)
- GCP services (GCS, BigQuery, Cloud Logging, Pub/Sub, Cloud Run, Vertex AI)
- Admin capabilities (Admin SDK)

All services use the MCP protocol and are ready to integrate with Claude Code!
