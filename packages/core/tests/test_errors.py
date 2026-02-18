from google_mcp_core.errors import MCPError, normalize_google_error


def test_normalize_passes_through_mcp_error():
    error = MCPError(code="x", message="y")
    assert normalize_google_error(error) is error


def test_normalize_unknown_error():
    error = ValueError("boom")
    normalized = normalize_google_error(error)
    assert normalized.code == "unknown_error"
    assert "boom" in normalized.message
