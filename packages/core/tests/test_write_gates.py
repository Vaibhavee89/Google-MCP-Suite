"""Every write tool must be gated; checked against the real service classes and server schemas.

The service packages are optional here: a missing one is skipped. Guards run before any
Google client is built, so none of these tests touch the network.
"""
import asyncio
import inspect

import pytest

from google_mcp_core.errors import MCPError
from google_mcp_core.safety import ALLOW_WRITES_ENV, READ_ONLY_ENV

# (module prefix, service class, tool prefix, {method: destructive}, [guard-only methods])
GATED = {
    "gmail": ("google_gmail_mcp", "GmailService", {
        "send_email": True, "reply_to_message": True, "trash_message": True, "delete_message": True}),
    "drive": ("google_drive_mcp", "DriveService", {
        "create_folder": False, "delete_file": True, "share_file": True, "move_file": True}),
    "calendar": ("google_calendar_mcp", "CalendarService", {"delete_event": True, "add_attendees": True}),
    "sheets": ("google_sheets_mcp", "SheetsService", {
        "update_values": False, "append_values": False, "batch_update": True, "create_spreadsheet": False,
        "add_sheet": False, "delete_sheet": True, "clear_values": True, "format_cells": False}),
    "docs": ("google_docs_mcp", "DocsService", {
        "create_document": False, "insert_text": False, "delete_text": True, "replace_text": False,
        "append_text": False, "format_text": False, "insert_image": False}),
    "forms": ("google_forms_mcp", "FormsService", {
        "create_form": False, "add_text_question": False, "add_multiple_choice_question": False,
        "add_checkbox_question": False, "update_form_info": False, "delete_item": True,
        "update_settings": False}),
    "tasks": ("google_tasks_mcp", "TasksService", {
        "create_task": False, "update_task": False, "delete_task": True, "complete_task": False,
        "create_task_list": False, "delete_task_list": True, "move_task": False}),
    "people": ("google_people_mcp", "PeopleService", {
        "create_contact": False, "update_contact": False, "delete_contact": True,
        "batch_create_contacts": False, "create_contact_group": False, "add_contact_to_group": False}),
}

# Writes that take no confirm parameter but must still honour read-only mode.
READ_ONLY_ONLY = {
    "gmail": ("google_gmail_mcp", "GmailService", ["create_draft", "modify_labels", "create_label",
                                                   "mark_as_read", "mark_as_unread"]),
    "drive": ("google_drive_mcp", "DriveService", ["upload_file", "copy_file", "update_file_metadata"]),
    "calendar": ("google_calendar_mcp", "CalendarService", ["create_event", "update_event",
                                                            "create_calendar", "quick_add_event"]),
    "slides": ("google_slides_mcp", "SlidesService", ["create_slide", "add_text_to_slide", "update_text",
                                                      "delete_slide", "create_presentation"]),
}


def _service(module, cls):
    mod = pytest.importorskip(f"{module}.service")
    return object.__new__(getattr(mod, cls))  # no config/auth needed: guards fire first


def _call_with_dummy_args(fn, **extra):
    sig = inspect.signature(fn)
    kwargs = {}
    for name, p in sig.parameters.items():
        if name == "self" or p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
            continue
        if p.default is inspect.Parameter.empty:
            kwargs[name] = [] if "list" in str(p.annotation).lower() else "x"
    kwargs.update(extra)
    return fn(**kwargs)


CASES = [(t, m, d) for t, (_, _, ms) in GATED.items() for m, d in ms.items()]


@pytest.mark.parametrize("tool,method,destructive", CASES)
def test_unconfirmed_call_is_refused(tool, method, destructive, monkeypatch):
    module, cls, _ = GATED[tool]
    fn = getattr(_service(module, cls), method)
    assert inspect.signature(fn).parameters["confirm"].default is False
    monkeypatch.delenv(READ_ONLY_ENV, raising=False)
    monkeypatch.setenv(ALLOW_WRITES_ENV, "1")
    with pytest.raises(MCPError) as exc:
        _call_with_dummy_args(fn)
    assert exc.value.code == "confirmation_required"
    if destructive:
        monkeypatch.delenv(ALLOW_WRITES_ENV)
        with pytest.raises(MCPError) as exc:
            _call_with_dummy_args(fn, confirm=True)
        assert exc.value.code == "writes_disabled"


@pytest.mark.parametrize("tool,method,destructive", CASES)
def test_read_only_refuses_confirmed_call(tool, method, destructive, monkeypatch):
    module, cls, _ = GATED[tool]
    fn = getattr(_service(module, cls), method)
    monkeypatch.setenv(READ_ONLY_ENV, "1")
    monkeypatch.setenv(ALLOW_WRITES_ENV, "1")
    with pytest.raises(MCPError) as exc:
        _call_with_dummy_args(fn, confirm=True)
    assert exc.value.code == "read_only"


RO_CASES = [(t, m) for t, (_, _, ms) in READ_ONLY_ONLY.items() for m in ms]


@pytest.mark.parametrize("tool,method", RO_CASES)
def test_read_only_refuses_ungated_writes(tool, method, monkeypatch):
    module, cls, _ = READ_ONLY_ONLY[tool]
    fn = getattr(_service(module, cls), method)
    monkeypatch.setenv(READ_ONLY_ENV, "1")
    with pytest.raises(MCPError) as exc:
        _call_with_dummy_args(fn)
    assert exc.value.code == "read_only"


def test_complete_task_forwards_confirm(monkeypatch):
    svc = _service("google_tasks_mcp", "TasksService")
    seen = {}
    svc.update_task = lambda *a, **k: seen.update(k) or {}
    monkeypatch.delenv(READ_ONLY_ENV, raising=False)
    svc.complete_task("l", "t", confirm=True)
    assert seen["confirm"] is True


@pytest.mark.parametrize("tool", sorted(GATED))
def test_server_schema_matches_service_signature(tool):
    module, cls, methods = GATED[tool]
    service_cls = getattr(pytest.importorskip(f"{module}.service"), cls)
    server = pytest.importorskip(f"{module}.server")
    tools = {t.name: t for t in asyncio.run(server.list_tools())}
    for method in methods:
        t = tools[f"{tool}_{method}"]
        assert "confirm" in t.inputSchema["properties"], t.name
        assert "confirm" in t.inputSchema["required"], t.name
        assert "confirm=true" in t.description, t.name
        assert "confirm" in inspect.signature(getattr(service_cls, method)).parameters
    # no read tool grew a confirm parameter
    for name, t in tools.items():
        if name.split("_", 1)[1] not in methods and "confirm" in t.inputSchema.get("properties", {}):
            pytest.fail(f"{name} unexpectedly has confirm")
