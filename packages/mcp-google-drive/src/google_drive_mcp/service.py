from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any, Dict, Optional

from googleapiclient.errors import HttpError

from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.client_factory import GoogleClientFactory
from google_mcp_core.config import AppConfig, load_config
from google_mcp_core.errors import MCPError, normalize_google_error
from google_mcp_core.retry import execute_with_retry
from google_mcp_core.safety import require_confirmation


READONLY_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
WRITE_SCOPES = ["https://www.googleapis.com/auth/drive"]


@dataclass
class DriveService:
    config: AppConfig
    auth_manager: AuthManager
    client_factory: GoogleClientFactory

    @classmethod
    def from_config(cls, config_path: Optional[str] = None) -> "DriveService":
        config = load_config(config_path)
        auth_manager = AuthManager(config)
        client_factory = GoogleClientFactory(auth_manager)
        return cls(config=config, auth_manager=auth_manager, client_factory=client_factory)

    def _client(self, scopes: list[str]) -> Any:
        return self.client_factory.get_client("drive", "v3", scopes)

    def _resolve_scopes(self, extra_scopes: Optional[list[str]] = None) -> list[str]:
        return self.auth_manager.resolve_scopes("drive", extra_scopes=extra_scopes)

    def _execute(self, request: Any) -> Any:
        return execute_with_retry(request.execute)

    def search_files(self, query: str, limit: int = 25, page_token: Optional[str] = None) -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            request = client.files().list(
                q=query,
                pageSize=limit,
                pageToken=page_token,
                fields="nextPageToken, files(id, name, mimeType, parents, size, modifiedTime, owners(emailAddress, displayName))",
            )
            response = self._execute(request)
            return {"items": response.get("files", []), "next_page_token": response.get("nextPageToken")}
        except Exception as exc:
            raise normalize_google_error(exc)

    def get_metadata(self, file_id: str) -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            request = client.files().get(
                fileId=file_id,
                fields="id, name, mimeType, parents, size, modifiedTime, owners(emailAddress, displayName)",
            )
            return self._execute(request)
        except Exception as exc:
            raise normalize_google_error(exc)

    def read_text(self, file_id: str) -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            metadata = self._execute(
                client.files().get(fileId=file_id, fields="id, name, mimeType")
            )
            mime_type = metadata.get("mimeType")
            if mime_type and mime_type.startswith("application/vnd.google-apps"):
                request = client.files().export(fileId=file_id, mimeType="text/plain")
            else:
                request = client.files().get_media(fileId=file_id)
            data = self._execute(request)
            if isinstance(data, bytes):
                text = data.decode("utf-8", errors="replace")
            else:
                text = str(data)
            return {"file_id": file_id, "name": metadata.get("name"), "mime_type": mime_type, "text": text}
        except Exception as exc:
            raise normalize_google_error(exc)

    def download(self, file_id: str) -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            metadata = self._execute(
                client.files().get(fileId=file_id, fields="id, name, mimeType, size")
            )
            request = client.files().get_media(fileId=file_id)
            content = self._execute(request)
            payload = content if isinstance(content, bytes) else str(content).encode("utf-8")
            encoded = base64.b64encode(payload).decode("ascii")
            return {
                "file_id": file_id,
                "name": metadata.get("name"),
                "mime_type": metadata.get("mimeType"),
                "size": metadata.get("size"),
                "content_base64": encoded,
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def list_children(self, folder_id: str, limit: int = 50, page_token: Optional[str] = None) -> Dict[str, Any]:
        query = f"'{folder_id}' in parents and trashed = false"
        return self.search_files(query=query, limit=limit, page_token=page_token)

    def get_permissions(self, file_id: str) -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            request = client.permissions().list(
                fileId=file_id,
                fields="permissions(id, type, role, emailAddress, displayName)",
            )
            response = self._execute(request)
            return {"items": response.get("permissions", [])}
        except Exception as exc:
            raise normalize_google_error(exc)

    def create_folder(self, name: str, parent_id: Optional[str] = None, confirm: bool = False) -> Dict[str, Any]:
        require_confirmation("drive.create_folder", confirm)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        body = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
        if parent_id:
            body["parents"] = [parent_id]
        try:
            request = client.files().create(body=body, fields="id, name")
            return self._execute(request)
        except Exception as exc:
            raise normalize_google_error(exc)
