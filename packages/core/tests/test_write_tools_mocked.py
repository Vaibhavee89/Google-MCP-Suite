"""Gmail / Drive / Calendar write tools against a mocked Google API client.

Covers: confirmation required, the operator switch, read-only mode, the exact API calls made
on the happy path, and retry behaviour end to end. Nothing here touches the network.
"""
import base64
import email

import pytest

from google_mcp_core.errors import MCPError

GMAIL = ("google_gmail_mcp", "GmailService")
DRIVE = ("google_drive_mcp", "DriveService")
CALENDAR = ("google_calendar_mcp", "CalendarService")

# (service, method, kwargs, needs GOOGLE_MCP_ALLOW_WRITES in addition to confirm=True)
GATED = [
    pytest.param(GMAIL, "send_email", dict(to="a@x.com", subject="s", body="b"), True, id="gmail_send_email"),
    pytest.param(GMAIL, "reply_to_message", dict(message_id="m1", body="b"), True, id="gmail_reply_to_message"),
    pytest.param(GMAIL, "trash_message", dict(message_id="m1"), True, id="gmail_trash_message"),
    pytest.param(GMAIL, "delete_message", dict(message_id="m1"), True, id="gmail_delete_message"),
    pytest.param(DRIVE, "delete_file", dict(file_id="f1"), True, id="drive_delete_file"),
    pytest.param(DRIVE, "share_file", dict(file_id="f1", email="a@x.com"), True, id="drive_share_file"),
    pytest.param(DRIVE, "move_file", dict(file_id="f1", new_parent_id="p2"), True, id="drive_move_file"),
    pytest.param(DRIVE, "create_folder", dict(name="n"), False, id="drive_create_folder"),
    pytest.param(CALENDAR, "delete_event", dict(event_id="e1"), True, id="calendar_delete_event"),
    pytest.param(CALENDAR, "add_attendees", dict(event_id="e1", attendees=["a@x.com"]), True, id="calendar_add_attendees"),
]

# Writes with no confirm parameter: they only honour read-only mode.
UNGATED = [
    pytest.param(GMAIL, "create_draft", dict(to="a@x.com", subject="s", body="b"), id="gmail_create_draft"),
    pytest.param(GMAIL, "modify_labels", dict(message_id="m1", add_labels=["STARRED"]), id="gmail_modify_labels"),
    pytest.param(GMAIL, "mark_as_read", dict(message_id="m1"), id="gmail_mark_as_read"),
    pytest.param(GMAIL, "mark_as_unread", dict(message_id="m1"), id="gmail_mark_as_unread"),
    pytest.param(GMAIL, "create_label", dict(name="L"), id="gmail_create_label"),
    pytest.param(DRIVE, "upload_file", dict(name="n", content="c"), id="drive_upload_file"),
    pytest.param(DRIVE, "copy_file", dict(file_id="f1"), id="drive_copy_file"),
    pytest.param(DRIVE, "update_file_metadata", dict(file_id="f1", name="n"), id="drive_update_file_metadata"),
    pytest.param(CALENDAR, "create_event", dict(summary="s", start_time="2026-01-01T10:00:00Z", end_time="2026-01-01T11:00:00Z"), id="calendar_create_event"),
    pytest.param(CALENDAR, "update_event", dict(event_id="e1", summary="s"), id="calendar_update_event"),
    pytest.param(CALENDAR, "create_calendar", dict(summary="s"), id="calendar_create_calendar"),
    pytest.param(CALENDAR, "quick_add_event", dict(text="lunch tomorrow"), id="calendar_quick_add_event"),
]


def _decode(raw: str):
    return email.message_from_bytes(base64.urlsafe_b64decode(raw))


# --- confirmation / operator switch / read-only -------------------------------------------

@pytest.mark.parametrize("svc_id,method,kwargs,needs_switch", GATED)
def test_confirmation_required(svc_id, method, kwargs, needs_switch, build_service, monkeypatch):
    monkeypatch.setenv("GOOGLE_MCP_ALLOW_WRITES", "1")
    service, _, factory = build_service(*svc_id)
    for confirm in ({}, {"confirm": False}):
        with pytest.raises(MCPError) as exc:
            getattr(service, method)(**kwargs, **confirm)
        assert exc.value.code == "confirmation_required"
    factory.get_client.assert_not_called()


@pytest.mark.parametrize("svc_id,method,kwargs,needs_switch", [p for p in GATED if p.values[3]])
def test_destructive_tools_need_operator_switch(svc_id, method, kwargs, needs_switch, build_service):
    service, _, factory = build_service(*svc_id)
    with pytest.raises(MCPError) as exc:
        getattr(service, method)(**kwargs, confirm=True)  # confirm alone is not enough
    assert exc.value.code == "writes_disabled"
    factory.get_client.assert_not_called()


@pytest.mark.parametrize("svc_id,method,kwargs,needs_switch", GATED)
def test_read_only_blocks_confirmed_writes(svc_id, method, kwargs, needs_switch, build_service, allow_writes, read_only_mode):
    service, _, factory = build_service(*svc_id)
    with pytest.raises(MCPError) as exc:
        getattr(service, method)(**kwargs, confirm=True)
    assert exc.value.code == "read_only"
    factory.get_client.assert_not_called()


@pytest.mark.parametrize("svc_id,method,kwargs", UNGATED)
def test_read_only_blocks_ungated_writes(svc_id, method, kwargs, build_service, read_only_mode):
    service, _, factory = build_service(*svc_id)
    with pytest.raises(MCPError) as exc:
        getattr(service, method)(**kwargs)
    assert exc.value.code == "read_only"
    factory.get_client.assert_not_called()


@pytest.mark.parametrize("svc_id,method,kwargs", UNGATED)
def test_ungated_writes_work_when_not_read_only(svc_id, method, kwargs, build_service):
    service, client, factory = build_service(*svc_id)
    getattr(service, method)(**kwargs)  # MagicMock client: just proves the guard lets it through
    factory.get_client.assert_called()


@pytest.mark.parametrize("svc_id,method", [(GMAIL, "search_messages"), (DRIVE, "search_files"), (CALENDAR, "search_events")])
def test_reads_still_work_in_read_only_mode(svc_id, method, build_service, read_only_mode):
    service, _, factory = build_service(*svc_id)
    getattr(service, method)(**({"query": "q"} if method != "search_events" else {}))
    factory.get_client.assert_called()


# --- happy paths: confirmed calls hit the right API with the right arguments --------------

def test_gmail_send_email(build_service, api, allow_writes):
    service, client, _ = build_service(*GMAIL)
    api(client, "users.messages.send").return_value.execute.return_value = {"id": "m9", "threadId": "t9"}
    result = service.send_email(to="a@x.com", subject="Hello", body="Body", cc="c@x.com", confirm=True)
    assert result == {"id": "m9", "thread_id": "t9", "message": "Email sent successfully"}
    kwargs = api(client, "users.messages.send").call_args.kwargs
    assert kwargs["userId"] == "me"
    msg = _decode(kwargs["body"]["raw"])
    assert (msg["to"], msg["subject"], msg["cc"]) == ("a@x.com", "Hello", "c@x.com")


def test_gmail_reply_to_message(build_service, api, allow_writes):
    service, client, _ = build_service(*GMAIL)
    api(client, "users.messages.get").return_value.execute.return_value = {
        "threadId": "t1",
        "payload": {"headers": [
            {"name": "From", "value": "bob@x.com"},
            {"name": "Subject", "value": "Lunch?"},
            {"name": "Message-ID", "value": "<abc@x.com>"},
        ]},
    }
    api(client, "users.messages.send").return_value.execute.return_value = {"id": "r1", "threadId": "t1"}
    result = service.reply_to_message(message_id="m1", body="Sure", confirm=True)
    assert result["id"] == "r1"
    api(client, "users.messages.get").assert_called_once_with(userId="me", id="m1", format="metadata")
    sent = api(client, "users.messages.send").call_args.kwargs["body"]
    assert sent["threadId"] == "t1"
    msg = _decode(sent["raw"])
    assert (msg["to"], msg["subject"], msg["In-Reply-To"]) == ("bob@x.com", "Re: Lunch?", "<abc@x.com>")


def test_gmail_trash_message(build_service, api, allow_writes):
    service, client, _ = build_service(*GMAIL)
    api(client, "users.messages.trash").return_value.execute.return_value = {"id": "m1"}
    assert service.trash_message("m1", confirm=True)["id"] == "m1"
    api(client, "users.messages.trash").assert_called_once_with(userId="me", id="m1")
    api(client, "users.messages.delete").assert_not_called()


def test_gmail_delete_message(build_service, api, allow_writes):
    service, client, _ = build_service(*GMAIL)
    assert service.delete_message("m1", confirm=True)["message_id"] == "m1"
    api(client, "users.messages.delete").assert_called_once_with(userId="me", id="m1")
    api(client, "users.messages.trash").assert_not_called()


def test_drive_delete_file(build_service, api, allow_writes):
    service, client, _ = build_service(*DRIVE)
    assert service.delete_file("f1", confirm=True)["file_id"] == "f1"
    api(client, "files.delete").assert_called_once_with(fileId="f1")


def test_drive_share_file(build_service, api, allow_writes):
    service, client, _ = build_service(*DRIVE)
    api(client, "permissions.create").return_value.execute.return_value = {
        "id": "perm1", "emailAddress": "a@x.com", "role": "writer"}
    result = service.share_file("f1", "a@x.com", role="writer", send_notification=False, confirm=True)
    assert result["permission_id"] == "perm1" and result["role"] == "writer"
    kwargs = api(client, "permissions.create").call_args.kwargs
    assert kwargs["fileId"] == "f1"
    assert kwargs["body"] == {"type": "user", "role": "writer", "emailAddress": "a@x.com"}
    assert kwargs["sendNotificationEmail"] is False


def test_drive_move_file(build_service, api, allow_writes):
    service, client, _ = build_service(*DRIVE)
    api(client, "files.get").return_value.execute.return_value = {"parents": ["old1", "old2"]}
    api(client, "files.update").return_value.execute.return_value = {"id": "f1", "name": "n", "parents": ["new"]}
    result = service.move_file("f1", "new", confirm=True)
    assert result["parents"] == ["new"]
    kwargs = api(client, "files.update").call_args.kwargs
    assert kwargs["fileId"] == "f1" and kwargs["addParents"] == "new" and kwargs["removeParents"] == "old1,old2"


def test_drive_create_folder_needs_only_confirm(build_service, api):
    service, client, _ = build_service(*DRIVE)  # no GOOGLE_MCP_ALLOW_WRITES set
    api(client, "files.create").return_value.execute.return_value = {"id": "d1", "name": "Docs"}
    assert service.create_folder("Docs", parent_id="root", confirm=True) == {"id": "d1", "name": "Docs"}
    body = api(client, "files.create").call_args.kwargs["body"]
    assert body["name"] == "Docs" and body["parents"] == ["root"]
    assert body["mimeType"] == "application/vnd.google-apps.folder"


def test_calendar_delete_event(build_service, api, allow_writes):
    service, client, _ = build_service(*CALENDAR)
    assert service.delete_event("e1", calendar_id="work", confirm=True)["event_id"] == "e1"
    api(client, "events.delete").assert_called_once_with(calendarId="work", eventId="e1")


def test_calendar_add_attendees_appends_to_existing(build_service, api, allow_writes):
    service, client, _ = build_service(*CALENDAR)
    api(client, "events.get").return_value.execute.return_value = {"id": "e1", "attendees": [{"email": "old@x.com"}]}
    api(client, "events.update").return_value.execute.return_value = {
        "id": "e1", "attendees": [{"email": "old@x.com"}, {"email": "new@x.com"}]}
    result = service.add_attendees("e1", ["new@x.com"], confirm=True)
    assert [a["email"] for a in result["attendees"]] == ["old@x.com", "new@x.com"]
    body = api(client, "events.update").call_args.kwargs["body"]
    assert [a["email"] for a in body["attendees"]] == ["old@x.com", "new@x.com"]


# --- retries, end to end through a service ------------------------------------------------

def test_service_call_survives_429_then_503(build_service, api, allow_writes, http_error, sleeps):
    service, client, _ = build_service(*GMAIL)
    execute = api(client, "users.messages.trash").return_value.execute
    execute.side_effect = [http_error(429), http_error(503), {"id": "m1"}]
    assert service.trash_message("m1", confirm=True)["id"] == "m1"
    assert execute.call_count == 3
    assert len(sleeps) == 2


def test_service_call_gives_up_and_normalises_error(build_service, api, allow_writes, http_error, sleeps):
    service, client, _ = build_service(*DRIVE)
    execute = api(client, "files.delete").return_value.execute
    execute.side_effect = [http_error(503)] * 10
    with pytest.raises(MCPError) as exc:
        service.delete_file("f1", confirm=True)
    assert exc.value.code == "google_http_503"
    assert execute.call_count == 4  # first try + 3 retries
    assert len(sleeps) == 3


def test_service_call_does_not_retry_client_errors(build_service, api, allow_writes, http_error, sleeps):
    service, client, _ = build_service(*CALENDAR)
    execute = api(client, "events.delete").return_value.execute
    execute.side_effect = [http_error(404)]
    with pytest.raises(MCPError) as exc:
        service.delete_event("e1", confirm=True)
    assert exc.value.code == "google_http_404"
    assert execute.call_count == 1
    assert sleeps == []
