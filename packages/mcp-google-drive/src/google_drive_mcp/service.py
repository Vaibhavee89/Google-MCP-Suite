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
FILE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]


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

    def upload_file(
        self,
        name: str,
        content: str,
        mime_type: str = "text/plain",
        parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload a file to Google Drive."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            from googleapiclient.http import MediaInMemoryUpload
            
            file_metadata = {"name": name}
            if parent_id:
                file_metadata["parents"] = [parent_id]
            
            media = MediaInMemoryUpload(
                content.encode('utf-8') if isinstance(content, str) else content,
                mimetype=mime_type,
                resumable=True
            )
            
            request = client.files().create(
                body=file_metadata,
                media_body=media,
                fields="id, name, mimeType, size"
            )
            result = self._execute(request)
            return {
                "file_id": result.get("id"),
                "name": result.get("name"),
                "mime_type": result.get("mimeType"),
                "size": result.get("size"),
                "message": "File uploaded successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def move_file(self, file_id: str, new_parent_id: str) -> Dict[str, Any]:
        """Move a file to a different folder."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            # Get current parents
            file = self._execute(client.files().get(fileId=file_id, fields="parents"))
            previous_parents = ",".join(file.get("parents", []))
            
            # Move file
            request = client.files().update(
                fileId=file_id,
                addParents=new_parent_id,
                removeParents=previous_parents,
                fields="id, name, parents"
            )
            result = self._execute(request)
            return {
                "file_id": result.get("id"),
                "name": result.get("name"),
                "parents": result.get("parents"),
                "message": "File moved successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def copy_file(self, file_id: str, new_name: Optional[str] = None) -> Dict[str, Any]:
        """Copy a file."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            body = {}
            if new_name:
                body["name"] = new_name
            
            request = client.files().copy(fileId=file_id, body=body, fields="id, name")
            result = self._execute(request)
            return {
                "file_id": result.get("id"),
                "name": result.get("name"),
                "message": "File copied successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def delete_file(self, file_id: str, confirm: bool = False) -> Dict[str, Any]:
        """Permanently delete a file (bypasses trash). Requires confirm=True."""
        require_confirmation("drive.delete_file", confirm, destructive=True)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            request = client.files().delete(fileId=file_id)
            self._execute(request)
            return {
                "file_id": file_id,
                "message": "File deleted successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def share_file(
        self,
        file_id: str,
        email: str,
        role: str = "reader",
        send_notification: bool = True,
        confirm: bool = False,
    ) -> Dict[str, Any]:
        """Share a file with a user. Requires confirm=True."""
        require_confirmation("drive.share_file", confirm, destructive=True)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            permission = {
                "type": "user",
                "role": role,
                "emailAddress": email
            }
            
            request = client.permissions().create(
                fileId=file_id,
                body=permission,
                sendNotificationEmail=send_notification,
                fields="id, type, role, emailAddress"
            )
            result = self._execute(request)
            return {
                "permission_id": result.get("id"),
                "email": result.get("emailAddress"),
                "role": result.get("role"),
                "message": f"File shared with {email} as {role}"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def update_file_metadata(
        self,
        file_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update file metadata."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            body = {}
            if name:
                body["name"] = name
            if description:
                body["description"] = description
            
            request = client.files().update(
                fileId=file_id,
                body=body,
                fields="id, name, description"
            )
            result = self._execute(request)
            return {
                "file_id": result.get("id"),
                "name": result.get("name"),
                "description": result.get("description"),
                "message": "File metadata updated successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)
