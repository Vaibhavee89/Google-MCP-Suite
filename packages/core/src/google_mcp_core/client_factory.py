from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.retry import execute_with_retry


@dataclass
class GoogleClientFactory:
    auth_manager: AuthManager
    cache: dict[tuple[str, str, tuple[str, ...]], object] = field(default_factory=dict)

    def get_client(
        self,
        service_name: str,
        version: str,
        scopes: list[str],
        cache_discovery: bool = False,
    ) -> object:
        cache_key = (service_name, version, tuple(scopes))
        if cache_key in self.cache:
            return self.cache[cache_key]
        credentials = self.auth_manager.get_credentials(service_name, scopes)
        service = execute_with_retry(
            lambda: build(service_name, version, credentials=credentials, cache_discovery=cache_discovery)
        )
        self.cache[cache_key] = service
        return service


def get_google_client(service_name: str, version: str, credentials: Credentials, cache_discovery: bool = False) -> object:
    return execute_with_retry(
        lambda: build(service_name, version, credentials=credentials, cache_discovery=cache_discovery)
    )
