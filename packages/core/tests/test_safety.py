import pytest

from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.config import AppConfig, GoogleConfig, OAuthConfig, ServiceAccountConfig
from google_mcp_core.errors import MCPError
from google_mcp_core.safety import ALLOW_WRITES_ENV, ScopeGuard, require_confirmation


def _config(allowed):
    return AppConfig(
        google=GoogleConfig(
            auth_mode="bogus",  # reaching this branch means the scope guard passed
            oauth=OAuthConfig("", "", "", ""),
            service_account=ServiceAccountConfig(""),
            allowed_scopes=allowed,
        )
    )


def test_require_confirmation_blocks_unconfirmed():
    with pytest.raises(MCPError) as exc:
        require_confirmation("x", False)
    assert exc.value.code == "confirmation_required"
    require_confirmation("x", True)


def test_scope_guard_empty_allowlist_allows_all():
    ScopeGuard().validate(["a", "b"])


def test_scope_guard_rejects_unlisted():
    with pytest.raises(MCPError) as exc:
        ScopeGuard({"a"}).validate(["a", "b"])
    assert exc.value.code == "scope_not_allowed"


def test_auth_manager_enforces_allowlist():
    with pytest.raises(MCPError) as exc:
        AuthManager(_config(["gmail.readonly"])).get_credentials("gmail", ["gmail.send"])
    assert exc.value.code == "scope_not_allowed"
    with pytest.raises(MCPError) as exc:
        AuthManager(_config([])).get_credentials("gmail", ["gmail.send"])
    assert exc.value.code == "invalid_auth_mode"


def test_destructive_requires_server_switch(monkeypatch):
    monkeypatch.delenv(ALLOW_WRITES_ENV, raising=False)
    with pytest.raises(MCPError) as exc:
        require_confirmation("x", True, destructive=True)
    assert exc.value.code == "writes_disabled"
    monkeypatch.setenv(ALLOW_WRITES_ENV, "1")
    with pytest.raises(MCPError) as exc:
        require_confirmation("x", False, destructive=True)
    assert exc.value.code == "confirmation_required"
    require_confirmation("x", True, destructive=True)


def test_non_destructive_ignores_switch(monkeypatch):
    monkeypatch.delenv(ALLOW_WRITES_ENV, raising=False)
    require_confirmation("x", True)
