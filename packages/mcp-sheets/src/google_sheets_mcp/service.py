from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.client_factory import GoogleClientFactory
from google_mcp_core.config import AppConfig, load_config
from google_mcp_core.errors import normalize_google_error
from google_mcp_core.retry import execute_with_retry


READONLY_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


@dataclass
class SheetsService:
    config: AppConfig
    auth_manager: AuthManager
    client_factory: GoogleClientFactory

    @classmethod
    def from_config(cls, config_path: Optional[str] = None) -> "SheetsService":
        config = load_config(config_path)
        auth_manager = AuthManager(config)
        client_factory = GoogleClientFactory(auth_manager)
        return cls(config=config, auth_manager=auth_manager, client_factory=client_factory)

    def _client(self, scopes: list[str]) -> Any:
        return self.client_factory.get_client("sheets", "v4", scopes)

    def _resolve_scopes(self, extra_scopes: Optional[list[str]] = None) -> list[str]:
        return self.auth_manager.resolve_scopes("sheets", extra_scopes=extra_scopes)

    def _execute(self, request: Any) -> Any:
        return execute_with_retry(request.execute)

    def read_range(
        self,
        spreadsheet_id: str,
        range_a1: str,
        major_dimension: str = "ROWS",
        value_render_option: str = "FORMATTED_VALUE",
    ) -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            request = client.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_a1,
                majorDimension=major_dimension,
                valueRenderOption=value_render_option,
            )
            response = self._execute(request)
            return {
                "range": response.get("range"),
                "major_dimension": response.get("majorDimension"),
                "values": response.get("values", []),
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def get_metadata(self, spreadsheet_id: str) -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            request = client.spreadsheets().get(
                spreadsheetId=spreadsheet_id,
                includeGridData=False,
            )
            return self._execute(request)
        except Exception as exc:
            raise normalize_google_error(exc)
