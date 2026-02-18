# Google MCP Suite Service Matrix

| Tier | Service | Auth Modes | API Client Library | Core Tools (MVP) | Rate-limit Gotchas |
| --- | --- | --- | --- | --- | --- |
| 1 | Google Drive | OAuth, Service Account (DWD) | google-api-python-client (Drive v3) | search_files, get_metadata, read_text, download, list_children, get_permissions, create_folder | 10 QPS/user; large exports throttled; use fields to reduce payload |
| 1 | Gmail | OAuth | google-api-python-client (Gmail v1) | search_messages, read_message | 250 QPS/user; label/message list rate limits |
| 1 | Calendar | OAuth, Service Account (DWD) | google-api-python-client (Calendar v3) | search_events, get_event | 10 QPS/user; use timeMin/timeMax filters |
| 1 | Sheets | OAuth, Service Account (DWD) | google-api-python-client (Sheets v4) | read_range, get_sheet_metadata | read requests batch; quota per project |
| 1 | Docs | OAuth, Service Account (DWD) | google-api-python-client (Docs v1) | export_text, get_document | export counts as read; large docs | 
| 1 | Meet | OAuth (limited), Admin (recording metadata) | google-api-python-client (Meet/Reports) | list_meetings, get_recording_metadata | Admin Reports quotas |
| 1 | GCS | Service Account | google-cloud-storage | list_objects, download_object, get_metadata | request-based pricing; GCS API QPS |
| 2 | Chat | OAuth, Admin | google-api-python-client (Chat v1) | list_spaces, search_messages | per-minute quotas |
| 2 | Forms | OAuth | google-api-python-client (Forms v1) | get_form, list_responses | low quotas; batching |
| 2 | Tasks/Keep | OAuth | google-api-python-client (Tasks v1) | list_tasks, get_task | per-user quotas |
| 2 | People | OAuth, Admin | google-api-python-client (People v1) | search_contacts, get_contact | field masks required |
| 2 | Admin SDK | Service Account (DWD) | google-api-python-client (Admin v1) | list_users, get_user | DWD + admin quotas |
| 3 | BigQuery | Service Account | google-cloud-bigquery | run_query, get_job, list_tables | job rate limits; per-project quotas |
| 3 | Logging/Monitoring | Service Account | google-cloud-logging, google-cloud-monitoring | list_entries, get_metrics | read quotas; pagination |
| 3 | Pub/Sub | Service Account | google-cloud-pubsub | list_topics, pull_messages | ack deadlines; retry |
| 3 | Cloud Functions/Run | Service Account | google-api-python-client (Cloud Functions v1), google-cloud-run | list_functions, get_service | admin-only; regional quotas |
| 3 | Vertex AI | Service Account | google-cloud-aiplatform | list_models, get_endpoint | high quotas but tight limits |

Notes:
- DWD = Domain-Wide Delegation.
- All services should use scope allowlists and least-privilege defaults.
