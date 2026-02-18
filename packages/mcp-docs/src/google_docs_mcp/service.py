from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.client_factory import GoogleClientFactory
from google_mcp_core.config import AppConfig, load_config
from google_mcp_core.errors import normalize_google_error
from google_mcp_core.retry import execute_with_retry


READONLY_SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]
DRIVE_READONLY_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


@dataclass
class DocsService:
    config: AppConfig
    auth_manager: AuthManager
    client_factory: GoogleClientFactory

    @classmethod
    def from_config(cls, config_path: Optional[str] = None) -> "DocsService":
        config = load_config(config_path)
        auth_manager = AuthManager(config)
        client_factory = GoogleClientFactory(auth_manager)
        return cls(config=config, auth_manager=auth_manager, client_factory=client_factory)

    def _docs_client(self, scopes: list[str]) -> Any:
        return self.client_factory.get_client("docs", "v1", scopes)

    def _drive_client(self, scopes: list[str]) -> Any:
        return self.client_factory.get_client("drive", "v3", scopes)

    def _resolve_scopes(self, extra_scopes: Optional[list[str]] = None) -> list[str]:
        return self.auth_manager.resolve_scopes("docs", extra_scopes=extra_scopes)

    def _execute(self, request: Any) -> Any:
        return execute_with_retry(request.execute)

    def get_document(self, document_id: str) -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._docs_client(scopes)
        try:
            request = client.documents().get(documentId=document_id)
            return self._execute(request)
        except Exception as exc:
            raise normalize_google_error(exc)

    def export_text(self, document_id: str) -> Dict[str, Any]:
        scopes = self._resolve_scopes(list(dict.fromkeys(READONLY_SCOPES + DRIVE_READONLY_SCOPES)))
        drive_client = self._drive_client(scopes)
        try:
            request = drive_client.files().export(fileId=document_id, mimeType="text/plain")
            data = self._execute(request)
            if isinstance(data, bytes):
                text = data.decode("utf-8", errors="replace")
            else:
                text = str(data)
            return {"document_id": document_id, "text": text}
        except Exception as exc:
            raise normalize_google_error(exc)
