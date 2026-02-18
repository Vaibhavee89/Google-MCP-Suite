from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.client_factory import GoogleClientFactory
from google_mcp_core.config import AppConfig, load_config
from google_mcp_core.errors import normalize_google_error
from google_mcp_core.retry import execute_with_retry


READONLY_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


@dataclass
class GmailService:
    config: AppConfig
    auth_manager: AuthManager
    client_factory: GoogleClientFactory

    @classmethod
    def from_config(cls, config_path: Optional[str] = None) -> "GmailService":
        config = load_config(config_path)
        auth_manager = AuthManager(config)
        client_factory = GoogleClientFactory(auth_manager)
        return cls(config=config, auth_manager=auth_manager, client_factory=client_factory)

    def _client(self, scopes: list[str]) -> Any:
        return self.client_factory.get_client("gmail", "v1", scopes)

    def _resolve_scopes(self, extra_scopes: Optional[list[str]] = None) -> list[str]:
        return self.auth_manager.resolve_scopes("gmail", extra_scopes=extra_scopes)

    def _execute(self, request: Any) -> Any:
        return execute_with_retry(request.execute)

    def search_messages(self, query: str, limit: int = 25, page_token: Optional[str] = None) -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            request = client.users().messages().list(
                userId="me",
                q=query,
                maxResults=limit,
                pageToken=page_token,
            )
            response = self._execute(request)
            return {
                "items": response.get("messages", []),
                "next_page_token": response.get("nextPageToken"),
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def read_message(self, message_id: str, format: str = "full") -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            request = client.users().messages().get(
                userId="me",
                id=message_id,
                format=format,
            )
            return self._execute(request)
        except Exception as exc:
            raise normalize_google_error(exc)
