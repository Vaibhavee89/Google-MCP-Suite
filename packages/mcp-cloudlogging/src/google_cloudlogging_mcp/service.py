from __future__ import annotations

from typing import Any, Optional

from google.cloud import logging
from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.config import load_config
from google_mcp_core.errors import handle_google_api_error


class CloudLoggingService:
    def __init__(self, auth_manager: AuthManager, project_id: Optional[str] = None):
        self.auth = auth_manager
        self.config = auth_manager.config
        self.project_id = project_id
        self._client = None

    @classmethod
    def from_config(cls, config_path: Optional[str] = None, project_id: Optional[str] = None) -> CloudLoggingService:
        config = load_config(config_path)
        auth_manager = AuthManager(config)
        return cls(auth_manager, project_id)

    def _get_client(self):
        if not self._client:
            service_config = self.config.services.get("cloudlogging")
            scopes = service_config.scopes if service_config else [
                "https://www.googleapis.com/auth/logging.read"
            ]
            creds = self.auth.get_credentials("cloudlogging", scopes)
            self._client = logging.Client(credentials=creds, project=self.project_id)
        return self._client

    @handle_google_api_error
    def list_logs(self, limit: int = 50) -> dict[str, Any]:
        client = self._get_client()
        logs = list(client.list_entries(max_results=limit, page_size=limit))
        
        return {
            "logs": [
                {
                    "log_name": entry.log_name,
                    "severity": entry.severity,
                    "timestamp": str(entry.timestamp),
                    "payload": str(entry.payload)[:200],
                }
                for entry in logs
            ]
        }

    @handle_google_api_error
    def query_logs(self, filter_str: str, limit: int = 100) -> dict[str, Any]:
        client = self._get_client()
        entries = list(client.list_entries(filter_=filter_str, max_results=limit))
        
        return {
            "entries": [
                {
                    "log_name": entry.log_name,
                    "severity": entry.severity,
                    "timestamp": str(entry.timestamp),
                    "resource": entry.resource._properties if entry.resource else None,
                    "payload": str(entry.payload),
                }
                for entry in entries
            ]
        }

    @handle_google_api_error
    def get_log_metrics(self) -> dict[str, Any]:
        client = self._get_client()
        metrics = list(client.list_metrics())
        
        return {
            "metrics": [
                {
                    "name": metric.name,
                    "description": metric.description,
                    "filter": metric.filter_,
                }
                for metric in metrics
            ]
        }
