# Testing Guide

## Unit Tests
- Core utilities live in `packages/core/tests`.
- Run with pytest from repo root:
  ```bash
  python -m pytest packages/core/tests
  ```

## Integration Tests (Optional)
- Use a dedicated Google Workspace test account.
- Export a config file and set:
  ```bash
  export GOOGLE_MCP_CONFIG=~/.google-mcp/config.yaml
  ```
- Run a single tool via the package server module, e.g.:
  ```bash
  python -m google_drive_mcp.server drive.search_files '{"query": "name contains \'Test\'"}'
  ```

## Safety
- Use readonly scopes for tests unless write access is required.
- Never run destructive tools without confirmation flags.
