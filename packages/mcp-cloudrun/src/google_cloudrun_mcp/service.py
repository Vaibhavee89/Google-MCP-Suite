from __future__ import annotations

from typing import Any, Optional

from google.cloud import run_v2
from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.config import load_config
from google_mcp_core.errors import handle_google_api_error


class CloudRunService:
    def __init__(self, auth_manager: AuthManager, project_id: Optional[str] = None, region: str = "us-central1"):
        self.auth = auth_manager
        self.config = auth_manager.config
        self.project_id = project_id
        self.region = region
        self._client = None

    @classmethod
    def from_config(cls, config_path: Optional[str] = None, project_id: Optional[str] = None, region: str = "us-central1") -> CloudRunService:
        config = load_config(config_path)
        auth_manager = AuthManager(config)
        return cls(auth_manager, project_id, region)

    def _get_client(self):
        if not self._client:
            service_config = self.config.services.get("cloudrun")
            scopes = service_config.scopes if service_config else [
                "https://www.googleapis.com/auth/cloud-platform.read-only"
            ]
            creds = self.auth.get_credentials("cloudrun", scopes)
            self._client = run_v2.ServicesClient(credentials=creds)
        return self._client

    @handle_google_api_error
    def list_services(self, limit: int = 50) -> dict[str, Any]:
        client = self._get_client()
        parent = f"projects/{self.project_id}/locations/{self.region}"
        
        services = []
        for service in client.list_services(parent=parent):
            services.append({
                "name": service.name,
                "uri": service.uri,
                "description": service.description,
                "generation": service.generation,
            })
            if len(services) >= limit:
                break
        
        return {"services": services}

    @handle_google_api_error
    def get_service(self, service_name: str) -> dict[str, Any]:
        client = self._get_client()
        name = f"projects/{self.project_id}/locations/{self.region}/services/{service_name}"
        service = client.get_service(name=name)
        
        return {
            "name": service.name,
            "uri": service.uri,
            "description": service.description,
            "generation": service.generation,
            "labels": dict(service.labels),
            "creator": service.creator,
            "last_modifier": service.last_modifier,
        }

    @handle_google_api_error
    def list_revisions(self, service_name: str, limit: int = 20) -> dict[str, Any]:
        client = self._get_client()
        parent = f"projects/{self.project_id}/locations/{self.region}/services/{service_name}"
        
        revisions = []
        for revision in client.list_revisions(parent=parent):
            revisions.append({
                "name": revision.name,
                "generation": revision.generation,
                "create_time": str(revision.create_time),
            })
            if len(revisions) >= limit:
                break
        
        return {"revisions": revisions}
