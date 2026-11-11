"""Shared fixtures: mocked Google API clients, no real sleeping, clean safety env."""
from unittest.mock import MagicMock

import httplib2
import pytest
from googleapiclient.errors import HttpError

from google_mcp_core.safety import ALLOW_WRITES_ENV, READ_ONLY_ENV


@pytest.fixture(autouse=True)
def clean_safety_env(monkeypatch):
    """Every test starts with neither GOOGLE_MCP_READ_ONLY nor GOOGLE_MCP_ALLOW_WRITES set."""
    monkeypatch.delenv(READ_ONLY_ENV, raising=False)
    monkeypatch.delenv(ALLOW_WRITES_ENV, raising=False)


@pytest.fixture(autouse=True)
def sleeps(monkeypatch):
    """Retry backoff never really sleeps; the requested delays are recorded here."""
    recorded: list[float] = []
    monkeypatch.setattr("google_mcp_core.retry.time.sleep", recorded.append)
    return recorded


@pytest.fixture
def allow_writes(monkeypatch):
    monkeypatch.setenv(ALLOW_WRITES_ENV, "1")


@pytest.fixture
def read_only_mode(monkeypatch):
    monkeypatch.setenv(READ_ONLY_ENV, "1")


@pytest.fixture
def http_error():
    def make(status: int) -> HttpError:
        return HttpError(httplib2.Response({"status": status}), b'{"error": "mocked"}')

    return make


@pytest.fixture
def build_service():
    """build_service(module, class_name) -> (service, google_client_mock, client_factory_mock).

    The service gets a MagicMock Google client and a MagicMock auth manager, so no
    credentials, config files or network are involved. Skips if the package isn't importable.
    """

    def build(module: str, cls: str):
        mod = pytest.importorskip(f"{module}.service")
        client = MagicMock(name="google_client")
        factory = MagicMock(name="client_factory")
        factory.get_client.return_value = client
        auth = MagicMock(name="auth_manager")
        auth.resolve_scopes.side_effect = lambda _name, extra_scopes=None: list(extra_scopes or [])
        service = getattr(mod, cls)(config=MagicMock(), auth_manager=auth, client_factory=factory)
        return service, client, factory

    return build


@pytest.fixture
def api():
    """api(client, "users.messages.send") -> the mock for that API method.

    Configure results with api(...).return_value.execute.return_value = {...} and
    inspect calls with api(...).assert_called_once_with(...).
    """

    def resolve(client, path: str) -> MagicMock:
        node = client
        for i, part in enumerate(path.split(".")):
            node = getattr(node, part)
            if i < len(path.split(".")) - 1:
                node = node.return_value
        return node

    return resolve
