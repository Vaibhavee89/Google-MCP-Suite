from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Iterable

from google_mcp_core.errors import MCPError


ALLOW_WRITES_ENV = "GOOGLE_MCP_ALLOW_WRITES"
READ_ONLY_ENV = "GOOGLE_MCP_READ_ONLY"
_TRUTHY = {"1", "true", "yes", "on"}


def writes_allowed() -> bool:
    """Server-side switch, set in the MCP server's environment (not by the agent)."""
    return os.environ.get(ALLOW_WRITES_ENV, "").strip().lower() in _TRUTHY


def read_only() -> bool:
    """Server-side read-only mode (GOOGLE_MCP_READ_ONLY=1): every write tool is refused."""
    return os.environ.get(READ_ONLY_ENV, "").strip().lower() in _TRUTHY


def require_writable(action: str) -> None:
    """Raise if the server is in read-only mode. Call from every write tool."""
    if read_only():
        raise MCPError(
            code="read_only",
            message=f"{action} is a write operation and the server is in read-only mode ({READ_ONLY_ENV}=1).",
        )


def require_confirmation(action: str, confirmed: bool, *, destructive: bool = False) -> None:
    """Gate an action behind confirm=True.

    With destructive=True the operator must also have enabled the server-side
    switch (GOOGLE_MCP_ALLOW_WRITES=1); an agent-supplied confirm alone is not enough.
    Read-only mode (GOOGLE_MCP_READ_ONLY=1) refuses the action regardless of confirm.
    """
    require_writable(action)
    if destructive and not writes_allowed():
        raise MCPError(
            code="writes_disabled",
            message=f"{action} is disabled. The server operator must set {ALLOW_WRITES_ENV}=1 to enable it.",
        )
    if not confirmed:
        raise MCPError(
            code="confirmation_required",
            message=f"Confirmation required to perform: {action}",
        )


@dataclass
class ScopeGuard:
    allowlist: set[str] = field(default_factory=set)

    def validate(self, scopes: Iterable[str]) -> None:
        missing = [scope for scope in scopes if self.allowlist and scope not in self.allowlist]
        if missing:
            raise MCPError(
                code="scope_not_allowed",
                message=f"Scopes not allowed: {', '.join(missing)}",
            )
