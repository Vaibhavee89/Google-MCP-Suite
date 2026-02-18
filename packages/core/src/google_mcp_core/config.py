from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional
import os

import yaml


DEFAULT_CONFIG_PATH = Path("~/.google-mcp/config.yaml").expanduser()


@dataclass
class OAuthConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    token_store: str


@dataclass
class ServiceAccountConfig:
    keyfile: str
    subject: Optional[str] = None


@dataclass
class GoogleConfig:
    auth_mode: str
    oauth: OAuthConfig
    service_account: ServiceAccountConfig
    default_scopes: list[str] = field(default_factory=list)


@dataclass
class ServiceConfig:
    enabled: bool = True
    scopes: list[str] = field(default_factory=list)


@dataclass
class AppConfig:
    google: GoogleConfig
    services: Dict[str, ServiceConfig] = field(default_factory=dict)


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _parse_google_config(payload: Dict[str, Any]) -> GoogleConfig:
    oauth_payload = payload.get("oauth", {})
    service_payload = payload.get("service_account", {})
    oauth = OAuthConfig(
        client_id=str(oauth_payload.get("client_id", "")),
        client_secret=str(oauth_payload.get("client_secret", "")),
        redirect_uri=str(oauth_payload.get("redirect_uri", "")),
        token_store=str(oauth_payload.get("token_store", "~/.google-mcp/tokens.json")),
    )
    service_account = ServiceAccountConfig(
        keyfile=str(service_payload.get("keyfile", "")),
        subject=service_payload.get("subject"),
    )
    return GoogleConfig(
        auth_mode=str(payload.get("auth_mode", "oauth")),
        oauth=oauth,
        service_account=service_account,
        default_scopes=list(payload.get("default_scopes", []) or []),
    )


def _parse_service_config(payload: Dict[str, Any]) -> ServiceConfig:
    return ServiceConfig(
        enabled=bool(payload.get("enabled", True)),
        scopes=list(payload.get("scopes", []) or []),
    )


def load_config(path: Optional[str] = None) -> AppConfig:
    env_path = os.environ.get("GOOGLE_MCP_CONFIG")
    config_path = Path(path or env_path or DEFAULT_CONFIG_PATH).expanduser()
    payload = _load_yaml(config_path)
    google_payload = payload.get("google", {})
    services_payload = payload.get("services", {})
    services = {
        name: _parse_service_config(data or {}) for name, data in services_payload.items()
    }
    return AppConfig(google=_parse_google_config(google_payload), services=services)


def resolve_scopes(config: AppConfig, service_name: str, extra_scopes: Optional[list[str]] = None) -> list[str]:
    service = config.services.get(service_name, ServiceConfig())
    scopes = list(dict.fromkeys(config.google.default_scopes + service.scopes))
    if extra_scopes:
        scopes.extend([scope for scope in extra_scopes if scope not in scopes])
    return scopes
