from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.client_factory import GoogleClientFactory
from google_mcp_core.config import AppConfig, load_config
from google_mcp_core.errors import normalize_google_error
from google_mcp_core.retry import execute_with_retry


REPORTS_SCOPES = ["https://www.googleapis.com/auth/admin.reports.audit.readonly"]


@dataclass
class MeetService:
    config: AppConfig
    auth_manager: AuthManager
    client_factory: GoogleClientFactory

    @classmethod
    def from_config(cls, config_path: Optional[str] = None) -> "MeetService":
        config = load_config(config_path)
        auth_manager = AuthManager(config)
        client_factory = GoogleClientFactory(auth_manager)
        return cls(config=config, auth_manager=auth_manager, client_factory=client_factory)

    def _client(self, scopes: list[str]) -> Any:
        return self.client_factory.get_client("admin", "reports_v1", scopes)

    def _resolve_scopes(self, extra_scopes: Optional[list[str]] = None) -> list[str]:
        return self.auth_manager.resolve_scopes("meet", extra_scopes=extra_scopes)

    def _execute(self, request: Any) -> Any:
        return execute_with_retry(request.execute)

    def list_activities(
        self,
        user_key: str = "all",
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 25,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        scopes = self._resolve_scopes(REPORTS_SCOPES)
        client = self._client(scopes)
        try:
            request = client.activities().list(
                userKey=user_key,
                applicationName="meet",
                startTime=start_time,
                endTime=end_time,
                maxResults=limit,
                pageToken=page_token,
            )
            response = self._execute(request)
            return {
                "items": response.get("items", []),
                "next_page_token": response.get("nextPageToken"),
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def get_activity(self, activity_id: str, user_key: str = "all") -> Dict[str, Any]:
        scopes = self._resolve_scopes(REPORTS_SCOPES)
        client = self._client(scopes)
        try:
            request = client.activities().get(
                userKey=user_key,
                applicationName="meet",
                activityId=activity_id,
            )
            return self._execute(request)
        except Exception as exc:
            raise normalize_google_error(exc)
