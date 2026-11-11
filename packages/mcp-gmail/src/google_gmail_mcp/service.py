from __future__ import annotations

import base64
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any, Dict, Optional

from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.client_factory import GoogleClientFactory
from google_mcp_core.config import AppConfig, load_config
from google_mcp_core.errors import normalize_google_error
from google_mcp_core.retry import execute_with_retry
from google_mcp_core.safety import require_confirmation, require_writable


READONLY_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
SEND_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
COMPOSE_SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]
MODIFY_SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


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

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        html: bool = False,
        confirm: bool = False,
    ) -> Dict[str, Any]:
        """Send an email. Requires confirm=True."""
        require_confirmation("gmail_send_email", confirm, destructive=True)
        scopes = self._resolve_scopes(SEND_SCOPES)
        client = self._client(scopes)
        try:
            message = MIMEMultipart() if html else MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc
            
            if html:
                message.attach(MIMEText(body, 'html'))
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            request = client.users().messages().send(
                userId='me',
                body={'raw': raw}
            )
            result = self._execute(request)
            return {
                "id": result.get("id"),
                "thread_id": result.get("threadId"),
                "message": "Email sent successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        html: bool = False
    ) -> Dict[str, Any]:
        """Create a draft email."""
        require_writable("gmail_create_draft")
        scopes = self._resolve_scopes(COMPOSE_SCOPES)
        client = self._client(scopes)
        try:
            message = MIMEMultipart() if html else MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            if cc:
                message['cc'] = cc
            
            if html:
                message.attach(MIMEText(body, 'html'))
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            request = client.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw}}
            )
            result = self._execute(request)
            return {
                "id": result.get("id"),
                "message": "Draft created successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def reply_to_message(
        self,
        message_id: str,
        body: str,
        html: bool = False,
        confirm: bool = False,
    ) -> Dict[str, Any]:
        """Reply to an email message. Requires confirm=True."""
        require_confirmation("gmail_reply_to_message", confirm, destructive=True)
        scopes = self._resolve_scopes(list(dict.fromkeys(READONLY_SCOPES + SEND_SCOPES)))
        client = self._client(scopes)
        try:
            original = self._execute(
                client.users().messages().get(userId='me', id=message_id, format='metadata')
            )
            thread_id = original.get('threadId')
            headers = {h['name']: h['value'] for h in original.get('payload', {}).get('headers', [])}
            
            message = MIMEText(body, 'html' if html else 'plain')
            message['to'] = headers.get('From', '')
            message['subject'] = 'Re: ' + headers.get('Subject', '')
            message['In-Reply-To'] = headers.get('Message-ID', '')
            message['References'] = headers.get('Message-ID', '')
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            request = client.users().messages().send(
                userId='me',
                body={'raw': raw, 'threadId': thread_id}
            )
            result = self._execute(request)
            return {
                "id": result.get("id"),
                "thread_id": result.get("threadId"),
                "message": "Reply sent successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def modify_labels(
        self,
        message_id: str,
        add_labels: Optional[list[str]] = None,
        remove_labels: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """Add or remove labels from a message."""
        require_writable("gmail_modify_labels")
        scopes = self._resolve_scopes(MODIFY_SCOPES)
        client = self._client(scopes)
        try:
            body = {}
            if add_labels:
                body['addLabelIds'] = add_labels
            if remove_labels:
                body['removeLabelIds'] = remove_labels
            
            request = client.users().messages().modify(
                userId='me',
                id=message_id,
                body=body
            )
            result = self._execute(request)
            return {
                "id": result.get("id"),
                "label_ids": result.get("labelIds", []),
                "message": "Labels modified successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def trash_message(self, message_id: str, confirm: bool = False) -> Dict[str, Any]:
        """Move a message to trash. Requires confirm=True."""
        require_confirmation("gmail_trash_message", confirm, destructive=True)
        scopes = self._resolve_scopes(MODIFY_SCOPES)
        client = self._client(scopes)
        try:
            request = client.users().messages().trash(userId='me', id=message_id)
            result = self._execute(request)
            return {
                "id": result.get("id"),
                "message": "Message moved to trash"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def delete_message(self, message_id: str, confirm: bool = False) -> Dict[str, Any]:
        """Permanently delete a message. Requires confirm=True."""
        require_confirmation("gmail_delete_message", confirm, destructive=True)
        scopes = self._resolve_scopes(MODIFY_SCOPES)
        client = self._client(scopes)
        try:
            request = client.users().messages().delete(userId='me', id=message_id)
            self._execute(request)
            return {
                "message_id": message_id,
                "message": "Message permanently deleted"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark a message as read."""
        return self.modify_labels(message_id, remove_labels=['UNREAD'])

    def mark_as_unread(self, message_id: str) -> Dict[str, Any]:
        """Mark a message as unread."""
        return self.modify_labels(message_id, add_labels=['UNREAD'])

    def list_labels(self) -> Dict[str, Any]:
        """List all labels."""
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            request = client.users().labels().list(userId='me')
            result = self._execute(request)
            return {
                "labels": [
                    {
                        "id": label.get("id"),
                        "name": label.get("name"),
                        "type": label.get("type")
                    }
                    for label in result.get("labels", [])
                ]
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def create_label(self, name: str, label_list_visibility: str = "labelShow", message_list_visibility: str = "show") -> Dict[str, Any]:
        """Create a new label."""
        require_writable("gmail_create_label")
        scopes = self._resolve_scopes(MODIFY_SCOPES)
        client = self._client(scopes)
        try:
            label_object = {
                "name": name,
                "labelListVisibility": label_list_visibility,
                "messageListVisibility": message_list_visibility
            }
            request = client.users().labels().create(userId='me', body=label_object)
            result = self._execute(request)
            return {
                "id": result.get("id"),
                "name": result.get("name"),
                "message": "Label created successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)
