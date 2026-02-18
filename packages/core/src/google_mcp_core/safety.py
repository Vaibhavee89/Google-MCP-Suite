from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional

from google_mcp_core.errors import MCPError


def require_confirmation(action: str, confirmed: bool) -> None:
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
