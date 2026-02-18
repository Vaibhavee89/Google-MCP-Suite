from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.client_factory import GoogleClientFactory
from google_mcp_core.config import AppConfig, load_config
from google_mcp_core.errors import normalize_google_error
from google_mcp_core.retry import execute_with_retry


CHAT_SCOPES = ["https://www.googleapis.com/auth/chat.messages.readonly"]


@dataclass
class ChatService:
    config: AppConfig
    auth_manager: AuthManager
    client_factory: GoogleClientFactory

    @classmethod
    def from_config(cls, config_path: Optional[str] = None) -> "ChatService":
        config = load_config(config_path)
        auth_manager = AuthManager(config)
        client_factory = GoogleClientFactory(auth_manager)
        return cls(config=config, auth_manager=auth_manager, client_factory=client_factory)

    def _client(self, scopes: list[str]) -> Any:
        return self.client_factory.get_client("chat", "v1", scopes)

    def _resolve_scopes(self, extra_scopes: Optional[list[str]] = None) -> list[str]:
        return self.auth_manager.resolve_scopes("chat", extra_scopes=extra_scopes)

    def _execute(self, request: Any) -> Any:
        return execute_with_retry(request.execute)

    def list_spaces(self, limit: int = 25, page_token: Optional[str] = None) -> Dict[str, Any]:
        scopes = self._resolve_scopes(CHAT_SCOPES)
        client = self._client(scopes)
        try:
            request = client.spaces().list(pageSize=limit, pageToken=page_token)
            response = self._execute(request)
            return {
                "items": response.get("spaces", []),
                "next_page_token": response.get("nextPageToken"),
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def search_messages(
        self,
        space: str,
        query: str,
        limit: int = 25,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        scopes = self._resolve_scopes(CHAT_SCOPES)
        client = self._client(scopes)
        try:
            request = client.spaces().messages().search(
                parent=space,
                query=query,
                pageSize=limit,
                pageToken=page_token,
            )
            response = self._execute(request)
            return {
                "items": response.get("messages", []),
                "next_page_token": response.get("nextPageToken"),
            }
        except Exception as exc:
            raise normalize_google_error(exc)
