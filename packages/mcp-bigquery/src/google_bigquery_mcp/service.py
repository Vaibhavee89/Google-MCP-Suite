from __future__ import annotations

from typing import Any, Optional

from google.cloud import bigquery
from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.config import load_config
from google_mcp_core.errors import handle_google_api_error


class BigQueryService:
    def __init__(self, auth_manager: AuthManager, project_id: Optional[str] = None):
        self.auth = auth_manager
        self.config = auth_manager.config
        self.project_id = project_id
        self._client = None

    @classmethod
    def from_config(cls, config_path: Optional[str] = None, project_id: Optional[str] = None) -> BigQueryService:
        config = load_config(config_path)
        auth_manager = AuthManager(config)
        return cls(auth_manager, project_id)

    def _get_client(self):
        if not self._client:
            service_config = self.config.services.get("bigquery")
            scopes = service_config.scopes if service_config else [
                "https://www.googleapis.com/auth/bigquery.readonly"
            ]
            creds = self.auth.get_credentials("bigquery", scopes)
            self._client = bigquery.Client(credentials=creds, project=self.project_id)
        return self._client

    @handle_google_api_error
    def list_datasets(self, limit: int = 50) -> dict[str, Any]:
        client = self._get_client()
        datasets = list(client.list_datasets(max_results=limit))
        
        return {
            "datasets": [
                {
                    "dataset_id": ds.dataset_id,
                    "project": ds.project,
                    "full_dataset_id": ds.full_dataset_id,
                }
                for ds in datasets
            ]
        }

    @handle_google_api_error
    def list_tables(self, dataset_id: str, limit: int = 100) -> dict[str, Any]:
        client = self._get_client()
        dataset_ref = client.dataset(dataset_id)
        tables = list(client.list_tables(dataset_ref, max_results=limit))
        
        return {
            "dataset_id": dataset_id,
            "tables": [
                {
                    "table_id": t.table_id,
                    "table_type": t.table_type,
                    "full_table_id": f"{t.project}.{t.dataset_id}.{t.table_id}",
                }
                for t in tables
            ]
        }

    @handle_google_api_error
    def get_table_schema(self, dataset_id: str, table_id: str) -> dict[str, Any]:
        client = self._get_client()
        table_ref = client.dataset(dataset_id).table(table_id)
        table = client.get_table(table_ref)
        
        return {
            "table_id": table.table_id,
            "num_rows": table.num_rows,
            "num_bytes": table.num_bytes,
            "schema": [
                {
                    "name": field.name,
                    "field_type": field.field_type,
                    "mode": field.mode,
                    "description": field.description,
                }
                for field in table.schema
            ]
        }

    @handle_google_api_error
    def query(self, sql: str, limit: int = 100) -> dict[str, Any]:
        client = self._get_client()
        query_job = client.query(sql)
        results = query_job.result(max_results=limit)
        
        rows = []
        for row in results:
            rows.append(dict(row))
        
        return {
            "rows": rows,
            "total_rows": results.total_rows,
            "schema": [
                {"name": field.name, "type": field.field_type}
                for field in results.schema
            ]
        }

    @handle_google_api_error
    def list_jobs(self, limit: int = 50) -> dict[str, Any]:
        client = self._get_client()
        jobs = list(client.list_jobs(max_results=limit))
        
        return {
            "jobs": [
                {
                    "job_id": job.job_id,
                    "state": job.state,
                    "job_type": job.job_type,
                    "created": str(job.created),
                }
                for job in jobs
            ]
        }
