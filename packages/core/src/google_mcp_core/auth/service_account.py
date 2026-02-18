from __future__ import annotations

from google.oauth2 import service_account
from google.oauth2.credentials import Credentials

from google_mcp_core.config import ServiceAccountConfig


def get_service_account_credentials(config: ServiceAccountConfig, scopes: list[str]) -> Credentials:
    credentials = service_account.Credentials.from_service_account_file(
        config.keyfile,
        scopes=scopes,
    )
    if config.subject:
        credentials = credentials.with_subject(config.subject)
    return credentials
