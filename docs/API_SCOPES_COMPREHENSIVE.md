# Google API Comprehensive Scopes & Capabilities

## Service Scope Matrix

### Google Drive
- **Read-only**: `https://www.googleapis.com/auth/drive.readonly`
- **Full access**: `https://www.googleapis.com/auth/drive`
- **File-specific**: `https://www.googleapis.com/auth/drive.file` (only files created by app)
- **Metadata**: `https://www.googleapis.com/auth/drive.metadata.readonly`

**Capabilities**:
- ✅ Read: search, get metadata, download, read text
- ✅ Write: upload, create folder, move, copy, delete, update, share

### Gmail
- **Read-only**: `https://www.googleapis.com/auth/gmail.readonly`
- **Send**: `https://www.googleapis.com/auth/gmail.send`
- **Compose**: `https://www.googleapis.com/auth/gmail.compose`
- **Modify**: `https://www.googleapis.com/auth/gmail.modify`
- **Full access**: `https://www.googleapis.com/auth/gmail.full`

**Capabilities**:
- ✅ Read: list messages, get message, search, get attachments
- ✅ Write: send email, create draft, modify labels, trash, delete

### Google Calendar
- **Read-only**: `https://www.googleapis.com/auth/calendar.readonly`
- **Full access**: `https://www.googleapis.com/auth/calendar`
- **Events**: `https://www.googleapis.com/auth/calendar.events`

**Capabilities**:
- ✅ Read: list events, get event, list calendars
- ✅ Write: create event, update event, delete event, create calendar

### Google Sheets
- **Read-only**: `https://www.googleapis.com/auth/spreadsheets.readonly`
- **Full access**: `https://www.googleapis.com/auth/spreadsheets`

**Capabilities**:
- ✅ Read: get values, get spreadsheet metadata
- ✅ Write: update values, append values, batch update, create spreadsheet, format cells

### Google Docs
- **Read-only**: `https://www.googleapis.com/auth/documents.readonly`
- **Full access**: `https://www.googleapis.com/auth/documents`

**Capabilities**:
- ✅ Read: get document, read content
- ✅ Write: create document, insert text, delete text, format text, insert images

### Google Slides
- **Read-only**: `https://www.googleapis.com/auth/presentations.readonly`
- **Full access**: `https://www.googleapis.com/auth/presentations`

**Capabilities**:
- ✅ Read: get presentation, get slide, list presentations, extract text
- ✅ Write: create presentation, create slide, add text, update text, delete slide, add images

### Google Forms
- **Read-only**: `https://www.googleapis.com/auth/forms.responses.readonly`
- **Body read**: `https://www.googleapis.com/auth/forms.body.readonly`
- **Full access**: `https://www.googleapis.com/auth/forms.body`

**Capabilities**:
- ✅ Read: get form, list responses, get response
- ✅ Write: create form, update form, add questions, delete questions

### Google Tasks
- **Read-only**: `https://www.googleapis.com/auth/tasks.readonly`
- **Full access**: `https://www.googleapis.com/auth/tasks`

**Capabilities**:
- ✅ Read: list task lists, list tasks, get task
- ✅ Write: create task, update task, delete task, move task, create task list

### People API (Contacts)
- **Read-only**: `https://www.googleapis.com/auth/contacts.readonly`
- **Full access**: `https://www.googleapis.com/auth/contacts`

**Capabilities**:
- ✅ Read: list contacts, get contact, search contacts
- ✅ Write: create contact, update contact, delete contact

### Google Meet
- **Read-only**: `https://www.googleapis.com/auth/admin.reports.audit.readonly`
- **Spaces**: `https://www.googleapis.com/auth/meetings.space.readonly`

**Capabilities**:
- ✅ Read: get meeting info, list recordings (via Admin SDK)
- ⚠️ Write: Limited - meeting creation typically done via Calendar API

### Admin SDK
- **Read-only**: `https://www.googleapis.com/auth/admin.directory.user.readonly`
- **User management**: `https://www.googleapis.com/auth/admin.directory.user`
- **Group read**: `https://www.googleapis.com/auth/admin.directory.group.readonly`
- **Group management**: `https://www.googleapis.com/auth/admin.directory.group`

**Capabilities**:
- ✅ Read: list users, get user, list groups, get group
- ✅ Write: create user, update user, delete user, create group, add members

### Google Chat
- **Read-only**: `https://www.googleapis.com/auth/chat.messages.readonly`
- **Send**: `https://www.googleapis.com/auth/chat.messages`
- **Spaces**: `https://www.googleapis.com/auth/chat.spaces`

**Capabilities**:
- ✅ Read: list messages, get message, list spaces
- ✅ Write: send message, create space, update space

### Google Cloud Storage (GCS)
- **Read-only**: `https://www.googleapis.com/auth/devstorage.read_only`
- **Read-write**: `https://www.googleapis.com/auth/devstorage.read_write`
- **Full control**: `https://www.googleapis.com/auth/devstorage.full_control`

**Capabilities**:
- ✅ Read: list buckets, list objects, get object, download
- ✅ Write: upload object, delete object, create bucket, set ACLs

### BigQuery
- **Read-only**: `https://www.googleapis.com/auth/bigquery.readonly`
- **Full access**: `https://www.googleapis.com/auth/bigquery`

**Capabilities**:
- ✅ Read: list datasets, list tables, get schema, query
- ✅ Write: create dataset, create table, insert data, run jobs

### Cloud Logging
- **Read**: `https://www.googleapis.com/auth/logging.read`
- **Write**: `https://www.googleapis.com/auth/logging.write`
- **Admin**: `https://www.googleapis.com/auth/logging.admin`

**Capabilities**:
- ✅ Read: list logs, query logs, get metrics
- ✅ Write: write log entries, create metrics, create sinks

### Pub/Sub
- **Full access**: `https://www.googleapis.com/auth/pubsub`

**Capabilities**:
- ✅ Read: list topics, get topic, list subscriptions, get subscription, pull messages
- ✅ Write: create topic, delete topic, publish messages, create subscription, acknowledge messages

### Cloud Run
- **Read-only**: `https://www.googleapis.com/auth/cloud-platform.read-only`
- **Full access**: `https://www.googleapis.com/auth/cloud-platform`

**Capabilities**:
- ✅ Read: list services, get service, list revisions
- ✅ Write: deploy service, update service, delete service

### Vertex AI
- **Full access**: `https://www.googleapis.com/auth/cloud-platform`

**Capabilities**:
- ✅ Read: list models, get model, list endpoints, get endpoint, list datasets
- ✅ Write: create model, deploy model, create endpoint, create dataset, train model

## Implementation Priority

### High Priority (User-facing productivity tools)
1. **Google Tasks** - Full CRUD operations
2. **Google Forms** - Create/edit forms and questions
3. **Gmail** - Send emails, create drafts, manage labels
4. **Calendar** - Create/update/delete events
5. **Sheets** - Update cells, create spreadsheets
6. **Docs** - Create/edit documents
7. **People API** - Create/update contacts

### Medium Priority (Collaboration & Admin)
8. **Drive** - Upload, move, share files
9. **Chat** - Send messages, create spaces
10. **Admin SDK** - User/group management

### Lower Priority (GCP Services)
11. **GCS** - Upload/delete objects
12. **BigQuery** - Create tables, insert data
13. **Pub/Sub** - Publish messages, create topics
14. **Cloud Logging** - Write logs, create metrics
15. **Cloud Run** - Deploy services
16. **Vertex AI** - Deploy models, create datasets
