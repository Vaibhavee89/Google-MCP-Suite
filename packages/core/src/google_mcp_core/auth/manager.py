from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from google.oauth2.credentials import Credentials

from google_mcp_core.auth.oauth import get_oauth_credentials
from google_mcp_core.auth.service_account import get_service_account_credentials
from google_mcp_core.auth.token_store import FileTokenStore, TokenStore
from google_mcp_core.config import AppConfig, resolve_scopes
from google_mcp_core.errors import MCPError
from google_mcp_core.safety import ScopeGuard


@dataclass
class AuthManager:
    config: AppConfig
    token_store: Optional[TokenStore] = None

    def get_credentials(self, service_name: str, scopes: list[str]) -> Credentials:
        ScopeGuard(set(self.config.google.allowed_scopes)).validate(scopes)
        auth_mode = self.config.google.auth_mode.lower()
        if auth_mode == "oauth":
            return get_oauth_credentials(
                self.config.google.oauth,
                scopes,
                token_store=self.token_store or FileTokenStore(self.config.google.oauth.token_store),
            )
        if auth_mode == "service_account":
            return get_service_account_credentials(self.config.google.service_account, scopes)
        raise MCPError(code="invalid_auth_mode", message=f"Unknown auth mode: {auth_mode}")

    def resolve_scopes(self, service_name: str, extra_scopes: Optional[list[str]] = None) -> list[str]:
        return resolve_scopes(self.config, service_name, extra_scopes=extra_scopes)
