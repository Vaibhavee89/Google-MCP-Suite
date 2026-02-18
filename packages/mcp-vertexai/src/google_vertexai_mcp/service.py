from __future__ import annotations

from typing import Any, Optional

from google.cloud import aiplatform
from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.config import load_config
from google_mcp_core.errors import handle_google_api_error


class VertexAIService:
    def __init__(self, auth_manager: AuthManager, project_id: Optional[str] = None, location: str = "us-central1"):
        self.auth = auth_manager
        self.config = auth_manager.config
        self.project_id = project_id
        self.location = location
        self._initialized = False

    @classmethod
    def from_config(cls, config_path: Optional[str] = None, project_id: Optional[str] = None, location: str = "us-central1") -> VertexAIService:
        config = load_config(config_path)
        auth_manager = AuthManager(config)
        return cls(auth_manager, project_id, location)

    def _init_aiplatform(self):
        if not self._initialized:
            service_config = self.config.services.get("vertexai")
            scopes = service_config.scopes if service_config else [
                "https://www.googleapis.com/auth/cloud-platform"
            ]
            creds = self.auth.get_credentials("vertexai", scopes)
            aiplatform.init(project=self.project_id, location=self.location, credentials=creds)
            self._initialized = True

    @handle_google_api_error
    def list_models(self, limit: int = 50) -> dict[str, Any]:
        self._init_aiplatform()
        models = aiplatform.Model.list()[:limit]
        
        return {
            "models": [
                {
                    "name": model.name,
                    "display_name": model.display_name,
                    "description": model.description,
                    "create_time": str(model.create_time),
                }
                for model in models
            ]
        }

    @handle_google_api_error
    def get_model(self, model_id: str) -> dict[str, Any]:
        self._init_aiplatform()
        model = aiplatform.Model(model_name=model_id)
        
        return {
            "name": model.name,
            "display_name": model.display_name,
            "description": model.description,
            "create_time": str(model.create_time),
            "update_time": str(model.update_time),
            "labels": dict(model.labels) if model.labels else {},
        }

    @handle_google_api_error
    def list_endpoints(self, limit: int = 50) -> dict[str, Any]:
        self._init_aiplatform()
        endpoints = aiplatform.Endpoint.list()[:limit]
        
        return {
            "endpoints": [
                {
                    "name": endpoint.name,
                    "display_name": endpoint.display_name,
                    "description": endpoint.description,
                    "create_time": str(endpoint.create_time),
                }
                for endpoint in endpoints
            ]
        }

    @handle_google_api_error
    def get_endpoint(self, endpoint_id: str) -> dict[str, Any]:
        self._init_aiplatform()
        endpoint = aiplatform.Endpoint(endpoint_name=endpoint_id)
        
        return {
            "name": endpoint.name,
            "display_name": endpoint.display_name,
            "description": endpoint.description,
            "create_time": str(endpoint.create_time),
            "update_time": str(endpoint.update_time),
        }

    @handle_google_api_error
    def list_datasets(self, limit: int = 50) -> dict[str, Any]:
        self._init_aiplatform()
        datasets = aiplatform.TabularDataset.list()[:limit]
        
        return {
            "datasets": [
                {
                    "name": dataset.name,
                    "display_name": dataset.display_name,
                    "create_time": str(dataset.create_time),
                }
                for dataset in datasets
            ]
        }
