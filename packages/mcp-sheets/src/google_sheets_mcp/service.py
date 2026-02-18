from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.client_factory import GoogleClientFactory
from google_mcp_core.config import AppConfig, load_config
from google_mcp_core.errors import normalize_google_error
from google_mcp_core.retry import execute_with_retry


READONLY_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
WRITE_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


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

    def update_values(
        self,
        spreadsheet_id: str,
        range_a1: str,
        values: list[list[Any]],
        value_input_option: str = "USER_ENTERED"
    ) -> Dict[str, Any]:
        """Update cell values in a spreadsheet."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            body = {"values": values}
            request = client.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_a1,
                valueInputOption=value_input_option,
                body=body
            )
            result = self._execute(request)
            return {
                "updated_range": result.get("updatedRange"),
                "updated_rows": result.get("updatedRows"),
                "updated_columns": result.get("updatedColumns"),
                "updated_cells": result.get("updatedCells"),
                "message": "Values updated successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def append_values(
        self,
        spreadsheet_id: str,
        range_a1: str,
        values: list[list[Any]],
        value_input_option: str = "USER_ENTERED"
    ) -> Dict[str, Any]:
        """Append rows to a spreadsheet."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            body = {"values": values}
            request = client.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_a1,
                valueInputOption=value_input_option,
                insertDataOption="INSERT_ROWS",
                body=body
            )
            result = self._execute(request)
            return {
                "updated_range": result.get("updates", {}).get("updatedRange"),
                "updated_rows": result.get("updates", {}).get("updatedRows"),
                "message": "Values appended successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def batch_update(
        self,
        spreadsheet_id: str,
        requests: list[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute batch update operations."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            body = {"requests": requests}
            request = client.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            )
            result = self._execute(request)
            return {
                "spreadsheet_id": result.get("spreadsheetId"),
                "replies": result.get("replies", []),
                "message": "Batch update completed successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def create_spreadsheet(
        self,
        title: str,
        sheets: Optional[list[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create a new spreadsheet."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            body = {"properties": {"title": title}}
            if sheets:
                body["sheets"] = sheets
            
            request = client.spreadsheets().create(body=body)
            result = self._execute(request)
            return {
                "spreadsheet_id": result.get("spreadsheetId"),
                "spreadsheet_url": result.get("spreadsheetUrl"),
                "title": result.get("properties", {}).get("title"),
                "message": "Spreadsheet created successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def add_sheet(
        self,
        spreadsheet_id: str,
        title: str,
        row_count: int = 1000,
        column_count: int = 26
    ) -> Dict[str, Any]:
        """Add a new sheet to a spreadsheet."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            requests = [{
                "addSheet": {
                    "properties": {
                        "title": title,
                        "gridProperties": {
                            "rowCount": row_count,
                            "columnCount": column_count
                        }
                    }
                }
            }]
            body = {"requests": requests}
            request = client.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            )
            result = self._execute(request)
            sheet_id = result.get("replies", [{}])[0].get("addSheet", {}).get("properties", {}).get("sheetId")
            return {
                "sheet_id": sheet_id,
                "title": title,
                "message": "Sheet added successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def delete_sheet(self, spreadsheet_id: str, sheet_id: int) -> Dict[str, Any]:
        """Delete a sheet from a spreadsheet."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            requests = [{"deleteSheet": {"sheetId": sheet_id}}]
            body = {"requests": requests}
            request = client.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            )
            self._execute(request)
            return {
                "sheet_id": sheet_id,
                "message": "Sheet deleted successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def clear_values(self, spreadsheet_id: str, range_a1: str) -> Dict[str, Any]:
        """Clear cell values in a range."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            request = client.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=range_a1
            )
            result = self._execute(request)
            return {
                "cleared_range": result.get("clearedRange"),
                "message": "Values cleared successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def format_cells(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        start_row: int,
        end_row: int,
        start_col: int,
        end_col: int,
        format_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format cells in a range."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            requests = [{
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": start_row,
                        "endRowIndex": end_row,
                        "startColumnIndex": start_col,
                        "endColumnIndex": end_col
                    },
                    "cell": {"userEnteredFormat": format_data},
                    "fields": "userEnteredFormat"
                }
            }]
            body = {"requests": requests}
            request = client.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            )
            self._execute(request)
            return {
                "message": "Cells formatted successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)
