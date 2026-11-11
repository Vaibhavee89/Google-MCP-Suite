from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.client_factory import GoogleClientFactory
from google_mcp_core.config import AppConfig, load_config
from google_mcp_core.errors import normalize_google_error
from google_mcp_core.retry import execute_with_retry
from google_mcp_core.safety import require_confirmation


READONLY_SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]
DRIVE_READONLY_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
WRITE_SCOPES = ["https://www.googleapis.com/auth/documents"]
DRIVE_FILE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]


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

    def create_document(self, title: str, confirm: bool = False) -> Dict[str, Any]:
        """Create a new Google Doc. Requires confirm=True."""
        require_confirmation("docs_create_document", confirm)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._docs_client(scopes)
        try:
            body = {"title": title}
            request = client.documents().create(body=body)
            result = self._execute(request)
            return {
                "document_id": result.get("documentId"),
                "title": result.get("title"),
                "message": "Document created successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def insert_text(self, document_id: str, text: str, index: int = 1, confirm: bool = False) -> Dict[str, Any]:
        """Insert text at a specific position in the document. Requires confirm=True."""
        require_confirmation("docs_insert_text", confirm)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._docs_client(scopes)
        try:
            requests = [{
                "insertText": {
                    "location": {"index": index},
                    "text": text
                }
            }]
            body = {"requests": requests}
            request = client.documents().batchUpdate(documentId=document_id, body=body)
            self._execute(request)
            return {
                "document_id": document_id,
                "message": "Text inserted successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def delete_text(self, document_id: str, start_index: int, end_index: int, confirm: bool = False) -> Dict[str, Any]:
        """Delete text from a document. Requires confirm=True."""
        require_confirmation("docs_delete_text", confirm, destructive=True)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._docs_client(scopes)
        try:
            requests = [{
                "deleteContentRange": {
                    "range": {
                        "startIndex": start_index,
                        "endIndex": end_index
                    }
                }
            }]
            body = {"requests": requests}
            request = client.documents().batchUpdate(documentId=document_id, body=body)
            self._execute(request)
            return {
                "document_id": document_id,
                "message": "Text deleted successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def replace_text(self, document_id: str, old_text: str, new_text: str, confirm: bool = False) -> Dict[str, Any]:
        """Replace all occurrences of text in a document. Requires confirm=True."""
        require_confirmation("docs_replace_text", confirm)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._docs_client(scopes)
        try:
            requests = [{
                "replaceAllText": {
                    "containsText": {
                        "text": old_text,
                        "matchCase": True
                    },
                    "replaceText": new_text
                }
            }]
            body = {"requests": requests}
            request = client.documents().batchUpdate(documentId=document_id, body=body)
            result = self._execute(request)
            occurrences = result.get("replies", [{}])[0].get("replaceAllText", {}).get("occurrencesChanged", 0)
            return {
                "document_id": document_id,
                "occurrences_changed": occurrences,
                "message": f"Replaced {occurrences} occurrences"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def append_text(self, document_id: str, text: str, confirm: bool = False) -> Dict[str, Any]:
        """Append text to the end of a document. Requires confirm=True."""
        require_confirmation("docs_append_text", confirm)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._docs_client(scopes)
        try:
            # Get document to find end index
            doc = self._execute(client.documents().get(documentId=document_id))
            end_index = doc.get("body", {}).get("content", [{}])[-1].get("endIndex", 1)
            
            requests = [{
                "insertText": {
                    "location": {"index": end_index - 1},
                    "text": text
                }
            }]
            body = {"requests": requests}
            request = client.documents().batchUpdate(documentId=document_id, body=body)
            self._execute(request)
            return {
                "document_id": document_id,
                "message": "Text appended successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def format_text(
        self,
        document_id: str,
        start_index: int,
        end_index: int,
        bold: Optional[bool] = None,
        italic: Optional[bool] = None,
        underline: Optional[bool] = None,
        font_size: Optional[int] = None,
        confirm: bool = False,
    ) -> Dict[str, Any]:
        """Format text in a document. Requires confirm=True."""
        require_confirmation("docs_format_text", confirm)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._docs_client(scopes)
        try:
            text_style = {}
            fields = []
            
            if bold is not None:
                text_style["bold"] = bold
                fields.append("bold")
            if italic is not None:
                text_style["italic"] = italic
                fields.append("italic")
            if underline is not None:
                text_style["underline"] = underline
                fields.append("underline")
            if font_size is not None:
                text_style["fontSize"] = {"magnitude": font_size, "unit": "PT"}
                fields.append("fontSize")
            
            requests = [{
                "updateTextStyle": {
                    "range": {
                        "startIndex": start_index,
                        "endIndex": end_index
                    },
                    "textStyle": text_style,
                    "fields": ",".join(fields)
                }
            }]
            body = {"requests": requests}
            request = client.documents().batchUpdate(documentId=document_id, body=body)
            self._execute(request)
            return {
                "document_id": document_id,
                "message": "Text formatted successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def insert_image(self, document_id: str, image_url: str, index: int = 1, confirm: bool = False) -> Dict[str, Any]:
        """Insert an image into a document. Requires confirm=True."""
        require_confirmation("docs_insert_image", confirm)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._docs_client(scopes)
        try:
            requests = [{
                "insertInlineImage": {
                    "location": {"index": index},
                    "uri": image_url
                }
            }]
            body = {"requests": requests}
            request = client.documents().batchUpdate(documentId=document_id, body=body)
            self._execute(request)
            return {
                "document_id": document_id,
                "message": "Image inserted successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)
