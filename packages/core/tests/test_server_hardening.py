"""Server-level behaviour shared by all 18 MCP servers.

Tool names are client-safe, failures surface as MCP errors (isError), the service is built
once per process, and every package ships a working console script. Servers whose Google
client libraries aren't installed are skipped.
"""
import asyncio
import importlib
import re
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from mcp.types import CallToolRequest, CallToolRequestParams

PACKAGES = Path(__file__).resolve().parents[2]
SERVERS = {
    "admin": "google_admin_sdk_mcp", "bigquery": "google_bigquery_mcp", "calendar": "google_calendar_mcp",
    "chat": "google_chat_mcp", "cloudlogging": "google_cloudlogging_mcp", "cloudrun": "google_cloudrun_mcp",
    "docs": "google_docs_mcp", "drive": "google_drive_mcp", "forms": "google_forms_mcp",
    "gcs": "google_gcs_mcp", "gmail": "google_gmail_mcp", "meet": "google_meet_mcp",
    "people": "google_people_mcp", "pubsub": "google_pubsub_mcp", "sheets": "google_sheets_mcp",
    "slides": "google_slides_mcp", "tasks": "google_tasks_mcp", "vertexai": "google_vertexai_mcp",
}
NAME_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")  # what MCP clients / the Claude API accept


def load_server(module: str):
    try:
        return importlib.import_module(f"{module}.server")
    except ImportError as exc:  # e.g. google-cloud-* client libraries not installed
        pytest.skip(f"{module} not importable here: {exc}")


def tools_of(server):
    return asyncio.run(server.list_tools())


def call_via_protocol(server, name, arguments=None):
    """Call a tool the way a client does, through the MCP request handler."""
    request = CallToolRequest(method="tools/call", params=CallToolRequestParams(name=name, arguments=arguments or {}))
    result = asyncio.run(server.app.request_handlers[CallToolRequest](request))
    return result.root


@pytest.fixture
def server_for(monkeypatch):
    """server_for(prefix, service=None): load a server with a clean _svc cache.

    With `service`, the server's _svc is replaced (restored automatically after the test).
    """
    originals = []

    def load(prefix, service=None):
        server = load_server(SERVERS[prefix])
        original = server._svc
        original.cache_clear()
        originals.append(original)
        if service is not None:
            monkeypatch.setattr(server, "_svc", lambda: service)
        return server

    yield load
    for original in originals:
        original.cache_clear()


# --- tool names --------------------------------------------------------------------------

@pytest.mark.parametrize("prefix", sorted(SERVERS))
def test_tool_names_are_client_safe(prefix):
    names = [t.name for t in tools_of(load_server(SERVERS[prefix]))]
    assert names and len(names) == len(set(names))
    for name in names:
        assert NAME_RE.match(name), f"{name!r} would be rejected by MCP clients"
        assert "." not in name
        assert name.startswith(f"{prefix}_"), name


@pytest.mark.parametrize("prefix", sorted(SERVERS))
def test_every_listed_tool_has_a_handler(prefix, server_for):
    service = MagicMock()
    server = server_for(prefix, service)  # handlers resolve through the module-level _svc
    for tool in tools_of(server):
        asyncio.run(server.call_tool(tool.name, {}))  # raises ValueError("Unknown tool") if not wired up
    assert service.method_calls, "no handler reached the service"


# --- errors are MCP errors ---------------------------------------------------------------

@pytest.mark.parametrize("prefix", sorted(SERVERS))
def test_unknown_tool_is_an_mcp_error(prefix, server_for):
    server = server_for(prefix, MagicMock())
    result = call_via_protocol(server, f"{prefix}_does_not_exist")
    assert result.isError is True
    assert "Unknown tool" in result.content[0].text


@pytest.mark.parametrize("prefix", sorted(SERVERS))
def test_old_dotted_names_are_gone(prefix, server_for):
    server = server_for(prefix, MagicMock())
    old_style = tools_of(server)[0].name.replace("_", ".", 1)
    result = call_via_protocol(server, old_style)
    assert result.isError is True
    assert "Unknown tool" in result.content[0].text


def test_safety_failures_are_error_results_not_text(server_for, monkeypatch):
    server = server_for("gmail")
    gmail = server.GmailService(config=MagicMock(), auth_manager=MagicMock(), client_factory=MagicMock())
    monkeypatch.setattr(server, "_svc", lambda: gmail)
    # no GOOGLE_MCP_ALLOW_WRITES -> writes_disabled
    result = call_via_protocol(server, "gmail_trash_message", {"message_id": "m1", "confirm": True})
    assert result.isError is True
    assert result.content[0].text.startswith("writes_disabled:")
    # operator switch on, but read-only mode wins
    monkeypatch.setenv("GOOGLE_MCP_ALLOW_WRITES", "1")
    monkeypatch.setenv("GOOGLE_MCP_READ_ONLY", "1")
    result = call_via_protocol(server, "gmail_trash_message", {"message_id": "m1", "confirm": True})
    assert result.isError is True
    assert result.content[0].text.startswith("read_only:")
    assert not result.content[0].text.startswith("Error:")


def test_unconfirmed_call_is_an_error_result(server_for, monkeypatch):
    server = server_for("calendar")
    calendar = server.CalendarService(config=MagicMock(), auth_manager=MagicMock(), client_factory=MagicMock())
    monkeypatch.setattr(server, "_svc", lambda: calendar)
    monkeypatch.setenv("GOOGLE_MCP_ALLOW_WRITES", "1")
    result = call_via_protocol(server, "calendar_delete_event", {"event_id": "e1", "confirm": False})
    assert result.isError is True
    assert result.content[0].text.startswith("confirmation_required:")


def test_success_is_not_an_error(server_for):
    service = MagicMock()
    service.list_labels.return_value = {"labels": [{"id": "INBOX"}]}
    server = server_for("gmail", service)
    result = call_via_protocol(server, "gmail_list_labels")
    assert result.isError is False
    assert '"INBOX"' in result.content[0].text


# --- service instance is cached ----------------------------------------------------------

@pytest.mark.parametrize("prefix", sorted(SERVERS))
def test_service_is_built_once(prefix, server_for, monkeypatch):
    server = server_for(prefix)
    (cls,) = [v for k, v in vars(server).items() if k.endswith("Service") and isinstance(v, type)]
    built = []
    monkeypatch.setattr(cls, "from_config", lambda *a, **k: built.append(1) or MagicMock())
    first, second = server._svc(), server._svc()
    assert first is second
    assert len(built) == 1


def test_failed_construction_is_retried_not_cached(server_for, monkeypatch):
    server = server_for("gmail")
    attempts = []

    def flaky(*a, **k):
        attempts.append(1)
        if len(attempts) == 1:
            raise RuntimeError("config not readable yet")
        return MagicMock()

    monkeypatch.setattr(server.GmailService, "from_config", flaky)
    with pytest.raises(RuntimeError):
        server._svc()
    assert server._svc() is server._svc()
    assert len(attempts) == 2


# --- console scripts ---------------------------------------------------------------------

@pytest.mark.parametrize("prefix", sorted(SERVERS))
def test_console_script_is_declared_and_importable(prefix):
    module = SERVERS[prefix]
    (pyproject,) = [p for p in PACKAGES.glob("mcp-*/pyproject.toml") if (p.parent / "src" / module).is_dir()]
    text = pyproject.read_text()
    scripts = re.search(r"^\[project\.scripts\]\n((?:[^\[\n].*\n)+)", text, re.M)
    assert scripts, f"{pyproject} has no [project.scripts]"
    entries = dict(re.findall(r'^([\w-]+) = "([\w.:]+)"$', scripts.group(1), re.M))
    server = load_server(module)
    assert entries == {server.app.name: f"{module}.server:run"}
    assert callable(importlib.import_module(f"{module}.server").run)
    assert 'build-backend = "setuptools.build_meta"' in text
