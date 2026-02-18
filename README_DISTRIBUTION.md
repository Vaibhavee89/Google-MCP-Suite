# Google MCP Suite - Complete Distribution Package

## 🎉 What's Included

This package contains a **complete Google Workspace automation suite** with 91 tools across 9 major Google services:

- **Gmail** (13 tools) - Send emails, manage labels, create drafts
- **Google Calendar** (10 tools) - Create/update events, manage calendars
- **Google Drive** (13 tools) - Upload, share, organize files
- **Google Sheets** (10 tools) - Update cells, create spreadsheets
- **Google Docs** (9 tools) - Create documents, edit text
- **Google Slides** (9 tools) - Create presentations, add slides
- **Google Tasks** (10 tools) - Manage tasks and task lists
- **Google Forms** (10 tools) - Create forms, add questions
- **People API** (9 tools) - Manage contacts, create groups

## 🚀 Quick Start (3 Steps)

### Step 1: Run Setup Script

```bash
chmod +x SETUP.sh
./SETUP.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Set up configuration directory
- Create helper scripts

### Step 2: Configure OAuth Credentials

1. **Get OAuth Credentials** from [Google Cloud Console](https://console.cloud.google.com/):
   - Create a new project (or use existing)
   - Enable required APIs (Drive, Gmail, Calendar, etc.)
   - Create OAuth 2.0 Client ID (Desktop application)
   - Download credentials

2. **Edit Configuration**:
   ```bash
   nano ~/.google-mcp/config.yaml
   ```

3. **Add Your Credentials**:
   ```yaml
   auth_mode: oauth
   oauth:
     client_id: "YOUR_CLIENT_ID_HERE"
     client_secret: "YOUR_CLIENT_SECRET_HERE"
     redirect_uri: "http://localhost:3080/gdrive/oauth/callback"
   ```

### Step 3: Authenticate

```bash
./authenticate.sh
```

This will open your browser for OAuth consent. Grant all requested permissions.

## ✅ You're Ready!

Test a service:
```bash
./test_server.sh drive
```

## 📋 System Requirements

- **Python**: 3.10 or higher
- **OS**: macOS, Linux, or Windows (with WSL)
- **Internet**: Required for Google API access
- **Browser**: For OAuth authentication

## 🔧 Installation Details

### What Gets Installed

The setup script installs:
- **Core package**: Common utilities, auth, error handling
- **9 MCP packages**: One for each Google service
- **Dependencies**: All required Python packages

### Directory Structure

```
MCP_Suite/
├── packages/
│   ├── core/                    # Core utilities
│   ├── mcp-drive/              # Google Drive MCP
│   ├── mcp-gmail/              # Gmail MCP
│   ├── mcp-calendar/           # Calendar MCP
│   ├── mcp-sheets/             # Sheets MCP
│   ├── mcp-docs/               # Docs MCP
│   ├── mcp-slides/             # Slides MCP
│   ├── mcp-forms/              # Forms MCP
│   ├── mcp-tasks/              # Tasks MCP
│   └── mcp-people/             # People API MCP
├── .venv/                       # Virtual environment
├── SETUP.sh                     # Setup script
├── authenticate.sh              # Auth helper
├── test_server.sh              # Test script
└── README_DISTRIBUTION.md      # This file
```

### Configuration Location

All configuration is stored in:
```
~/.google-mcp/
├── config.yaml      # Configuration file
└── tokens.json      # OAuth tokens (created after auth)
```

## 🔐 OAuth Setup Guide

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Note your project ID

### 2. Enable APIs

Enable these APIs in your project:
- Google Drive API
- Gmail API
- Google Calendar API
- Google Sheets API
- Google Docs API
- Google Slides API
- Google Forms API
- Google Tasks API
- People API (Contacts)

Quick link: [API Library](https://console.cloud.google.com/apis/library)

### 3. Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Choose **Desktop app** as application type
4. Name it (e.g., "Google MCP Suite")
5. Download the JSON file

### 4. Configure OAuth Consent Screen

1. Go to **OAuth consent screen**
2. Choose **External** (unless you have Google Workspace)
3. Fill in required fields:
   - App name: "Google MCP Suite"
   - User support email: Your email
   - Developer contact: Your email
4. Add scopes (or skip - they'll be requested dynamically)
5. Add test users (your email)

### 5. Add Credentials to Config

Copy the `client_id` and `client_secret` from the downloaded JSON to `~/.google-mcp/config.yaml`.

## 🎯 Using with Claude Code

After setup and authentication, add services to Claude Code:

```bash
# Add Google Drive
claude mcp add google-drive -- /path/to/MCP_Suite/.venv/bin/python -m google_drive_mcp.server

# Add Gmail
claude mcp add google-gmail -- /path/to/MCP_Suite/.venv/bin/python -m google_gmail_mcp.server

# Add Calendar
claude mcp add google-calendar -- /path/to/MCP_Suite/.venv/bin/python -m google_calendar_mcp.server

# Add Sheets
claude mcp add google-sheets -- /path/to/MCP_Suite/.venv/bin/python -m google_sheets_mcp.server

# Add Docs
claude mcp add google-docs -- /path/to/MCP_Suite/.venv/bin/python -m google_docs_mcp.server

# Add Slides
claude mcp add google-slides -- /path/to/MCP_Suite/.venv/bin/python -m google_slides_mcp.server

# Add Forms
claude mcp add google-forms -- /path/to/MCP_Suite/.venv/bin/python -m google_forms_mcp.server

# Add Tasks
claude mcp add google-tasks -- /path/to/MCP_Suite/.venv/bin/python -m google_tasks_mcp.server

# Add People (Contacts)
claude mcp add google-people -- /path/to/MCP_Suite/.venv/bin/python -m google_people_mcp.server
```

Replace `/path/to/MCP_Suite` with the actual path where you extracted the package.

## 🛠️ Troubleshooting

### "No module named 'google_mcp_core'"

Run the setup script again:
```bash
./SETUP.sh
```

### "Authentication failed"

1. Check your OAuth credentials in `~/.google-mcp/config.yaml`
2. Ensure redirect URI is: `http://localhost:3080/gdrive/oauth/callback`
3. Delete tokens and re-authenticate:
   ```bash
   rm ~/.google-mcp/tokens.json
   ./authenticate.sh
   ```

### "Permission denied" errors

Grant all permissions in the OAuth consent screen. You may need to:
1. Delete `~/.google-mcp/tokens.json`
2. Run `./authenticate.sh` again
3. Grant ALL requested permissions

### APIs not enabled

Enable all required APIs in Google Cloud Console:
- [API Library](https://console.cloud.google.com/apis/library)

### Test users not added

If you're using an external OAuth consent screen, add your email as a test user:
- Go to **OAuth consent screen** → **Test users** → **Add users**

## 📚 Documentation

- **100_PERCENT_COMPLETE.md** - Complete feature list (91 tools!)
- **COMPLETE_IMPLEMENTATION_SUMMARY.md** - Detailed implementation breakdown
- **docs/claude-code-setup.md** - Claude Code integration guide
- **docs/config.example.yaml** - Configuration template with comments

## 🎨 Available Tools by Service

### Gmail (13 tools)
- search_messages, read_message, list_labels
- send_email, create_draft, reply_to_message
- modify_labels, trash_message, delete_message
- mark_as_read, mark_as_unread, create_label

### Calendar (10 tools)
- search_events, get_event, list_calendars
- create_event, update_event, delete_event
- create_calendar, add_attendees, quick_add_event

### Drive (13 tools)
- search_files, get_metadata, read_text, download
- list_children, get_permissions
- upload_file, create_folder, move_file, copy_file
- delete_file, share_file, update_file_metadata

### Sheets (10 tools)
- read_range, get_metadata
- update_values, append_values, batch_update
- create_spreadsheet, add_sheet, delete_sheet
- clear_values, format_cells

### Docs (9 tools)
- get_document, export_text
- create_document, insert_text, delete_text
- replace_text, append_text, format_text, insert_image

### Slides (9 tools)
- get_presentation, get_slide_content, list_presentations, extract_text
- create_presentation, create_slide, add_text_to_slide
- update_text, delete_slide

### Forms (10 tools)
- get_form, list_responses, get_response
- create_form, add_text_question, add_multiple_choice_question
- add_checkbox_question, update_form_info, delete_item, update_settings

### Tasks (10 tools)
- list_task_lists, list_tasks, get_task
- create_task, update_task, delete_task, complete_task
- create_task_list, delete_task_list, move_task

### People/Contacts (9 tools)
- list_contacts, get_contact, search_contacts
- create_contact, update_contact, delete_contact
- batch_create_contacts, create_contact_group, add_contact_to_group

## 🔒 Security Notes

### Credentials Safety

- **Never commit** `config.yaml` with real credentials to version control
- **Never share** your `tokens.json` file
- **Keep** your OAuth client secret private
- **Use** test users during development

### OAuth Scopes

This suite requests comprehensive scopes for full functionality:
- Drive: Full access (read, write, file management)
- Gmail: Send, compose, modify
- Calendar: Full access
- Sheets, Docs, Slides: Full access
- Forms: Body access (read/write)
- Tasks: Full access
- Contacts: Full access

Only grant these permissions if you trust the application.

### Token Storage

OAuth tokens are stored at `~/.google-mcp/tokens.json`. This file contains sensitive access tokens. Protect it with appropriate file permissions:

```bash
chmod 600 ~/.google-mcp/tokens.json
```

## 🤝 Support

### Common Issues

1. **Import errors**: Run `./SETUP.sh` again
2. **Auth errors**: Check OAuth credentials and redirect URI
3. **Permission errors**: Grant all scopes in OAuth consent
4. **API errors**: Enable all required APIs in Google Cloud Console

### Getting Help

- Check the troubleshooting section above
- Review the documentation files
- Ensure all prerequisites are met
- Verify OAuth setup is complete

## 📄 License

This project uses the MIT License. See LICENSE file for details.

## 🎉 Enjoy!

You now have a comprehensive Google Workspace automation suite with 91 tools across 9 services. Use it with Claude Code for powerful productivity automation!

**Happy Automating!** 🚀
