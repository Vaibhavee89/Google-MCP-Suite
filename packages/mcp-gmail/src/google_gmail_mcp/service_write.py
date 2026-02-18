"""Gmail write operations - to be merged into service.py"""
from __future__ import annotations

import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any, Dict, Optional, List


def send_email(
    self,
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    html: bool = False
) -> Dict[str, Any]:
    """Send an email."""
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
    html: bool = False
) -> Dict[str, Any]:
    """Reply to an email message."""
    scopes = self._resolve_scopes(list(dict.fromkeys(READONLY_SCOPES + SEND_SCOPES)))
    client = self._client(scopes)
    try:
        # Get original message to extract thread ID and headers
        original = self._execute(
            client.users().messages().get(userId='me', id=message_id, format='metadata')
        )
        thread_id = original.get('threadId')
        headers = {h['name']: h['value'] for h in original.get('payload', {}).get('headers', [])}
        
        # Create reply
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
    add_labels: Optional[List[str]] = None,
    remove_labels: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Add or remove labels from a message."""
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


def trash_message(self, message_id: str) -> Dict[str, Any]:
    """Move a message to trash."""
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


def delete_message(self, message_id: str) -> Dict[str, Any]:
    """Permanently delete a message."""
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
