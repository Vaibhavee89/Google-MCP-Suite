from google_mcp_core.config import AppConfig, GoogleConfig, OAuthConfig, ServiceAccountConfig, ServiceConfig, resolve_scopes


def test_resolve_scopes_merges_defaults():
    config = AppConfig(
        google=GoogleConfig(
            auth_mode="oauth",
            oauth=OAuthConfig("id", "secret", "uri", "token"),
            service_account=ServiceAccountConfig("key"),
            default_scopes=["scope-a"],
        ),
        services={"drive": ServiceConfig(scopes=["scope-b"])},
    )
    scopes = resolve_scopes(config, "drive")
    assert scopes == ["scope-a", "scope-b"]
