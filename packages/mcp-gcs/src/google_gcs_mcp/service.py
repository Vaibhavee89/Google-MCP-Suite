from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any, Dict, Optional

from google.cloud import storage

from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.config import AppConfig, load_config
from google_mcp_core.errors import MCPError, normalize_google_error


READONLY_SCOPES = ["https://www.googleapis.com/auth/devstorage.read_only"]


@dataclass
class GCSService:
    config: AppConfig
    auth_manager: AuthManager

    @classmethod
    def from_config(cls, config_path: Optional[str] = None) -> "GCSService":
        config = load_config(config_path)
        auth_manager = AuthManager(config)
        return cls(config=config, auth_manager=auth_manager)

    def _client(self, scopes: list[str]) -> storage.Client:
        credentials = self.auth_manager.get_credentials("gcs", scopes)
        return storage.Client(credentials=credentials)

    def _resolve_scopes(self, extra_scopes: Optional[list[str]] = None) -> list[str]:
        return self.auth_manager.resolve_scopes("gcs", extra_scopes=extra_scopes)

    def list_objects(
        self,
        bucket_name: str,
        prefix: Optional[str] = None,
        limit: int = 100,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            iterator = client.list_blobs(
                bucket_name,
                prefix=prefix,
                max_results=limit,
                page_token=page_token,
            )
            page = next(iterator.pages)
            items = [
                {
                    "name": blob.name,
                    "size": blob.size,
                    "content_type": blob.content_type,
                    "updated": blob.updated.isoformat() if blob.updated else None,
                    "md5_hash": blob.md5_hash,
                    "bucket": blob.bucket.name,
                }
                for blob in page
            ]
            return {"items": items, "next_page_token": iterator.next_page_token}
        except Exception as exc:
            raise normalize_google_error(exc)

    def get_object_metadata(self, bucket_name: str, object_name: str) -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            blob = client.bucket(bucket_name).get_blob(object_name)
            if not blob:
                raise MCPError(code="not_found", message="Object not found")
            return {
                "name": blob.name,
                "size": blob.size,
                "content_type": blob.content_type,
                "updated": blob.updated.isoformat() if blob.updated else None,
                "md5_hash": blob.md5_hash,
                "bucket": blob.bucket.name,
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def download_object(self, bucket_name: str, object_name: str) -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            blob = client.bucket(bucket_name).blob(object_name)
            payload = blob.download_as_bytes()
            encoded = base64.b64encode(payload).decode("ascii")
            return {
                "name": blob.name,
                "bucket": bucket_name,
                "content_base64": encoded,
            }
        except Exception as exc:
            raise normalize_google_error(exc)
