# MCP Client Configuration Guide

This guide shows how to connect MCP clients to the Google Calendar HTTP server.

## Prerequisites

1. Start the HTTP server:
   ```bash
   python run_http_server.py 8000
   ```

2. Verify the server is running:
   ```bash
   curl http://localhost:8000/health
   # Should return: ok
   ```

## Claude Desktop Configuration

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "google-calendar": {
      "transport": {
        "type": "http",
        "url": "http://localhost:8000/mcp"
      }
    }
  }
}
```

## Cline Configuration (VS Code Extension)

In VS Code settings or `.vscode/settings.json`:

```json
{
  "cline.mcpServers": {
    "google-calendar": {
      "transport": {
        "type": "http",
        "url": "http://localhost:8000/mcp"
      }
    }
  }
}
```

## MCP Inspector Configuration

```bash
# Using npx (recommended for testing)
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

## Custom MCP Client Configuration

For any MCP-compatible client, use these settings:

- **Transport Type**: HTTP/SSE
- **URL**: `http://localhost:8000/mcp`
- **Methods**: GET (SSE), POST (requests), DELETE (session cleanup)

## Testing the Connection

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# List available tools (requires proper MCP request format)
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

### Using the MCP Inspector

1. Start the HTTP server:
   ```bash
   python run_http_server.py 8000
   ```

2. Launch MCP Inspector:
   ```bash
   npx @modelcontextprotocol/inspector http://localhost:8000/mcp
   ```

3. Test available tools through the web interface

## Production Deployment

### Using systemd (Linux)

Create `/etc/systemd/system/google-calendar-mcp.service`:

```ini
[Unit]
Description=Google Calendar MCP Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/MCP_Suite/packages/mcp-calendar
ExecStart=/usr/bin/python3 run_http_server.py 8000 0.0.0.0
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable google-calendar-mcp
sudo systemctl start google-calendar-mcp
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY src/ src/
COPY run_http_server.py .

# Install dependencies
RUN pip install -e .

# Expose port
EXPOSE 8000

# Run server
CMD ["python", "run_http_server.py", "8000", "0.0.0.0"]
```

Build and run:
```bash
docker build -t google-calendar-mcp .
docker run -p 8000:8000 google-calendar-mcp
```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  google-calendar-mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
    volumes:
      - ./credentials.json:/app/credentials.json:ro
      - ./tokens:/root/.config/google-mcp-core/tokens
    restart: unless-stopped
```

Run:
```bash
docker-compose up -d
```

## Security Considerations

⚠️ **Important Security Notes:**

1. **Local Development Only**: By default, the server binds to `0.0.0.0` which accepts connections from any network interface. For production:
   - Bind to `127.0.0.1` (localhost only)
   - Use a reverse proxy (nginx, caddy) with HTTPS
   - Implement authentication/authorization

2. **OAuth Credentials**: Never expose your OAuth credentials
   - Store `credentials.json` securely
   - Add to `.gitignore`
   - Use environment variables in production

3. **Network Security**:
   - Use HTTPS in production
   - Implement rate limiting
   - Use firewall rules to restrict access

## Firewall Configuration

Allow only local connections:

```bash
# Linux (ufw)
sudo ufw allow from 127.0.0.1 to any port 8000

# macOS (pf)
# Add to /etc/pf.conf:
# pass in proto tcp from 127.0.0.1 to any port 8000
```

## Troubleshooting

### Connection Refused

1. Check if server is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check which port the server is using:
   ```bash
   lsof -i :8000
   ```

3. Check firewall rules

### Authentication Errors

1. Verify OAuth credentials are present
2. Check token expiration
3. Re-authenticate if needed:
   ```bash
   # Remove cached tokens
   rm -rf ~/.config/google-mcp-core/tokens/*
   # Restart server (will trigger re-auth)
   python run_http_server.py 8000
   ```

### MCP Client Can't Connect

1. Verify the URL in client config matches server address
2. Check server logs for errors
3. Test with curl to isolate the issue
4. Ensure MCP client supports HTTP/SSE transport

## Advanced Configuration

### Custom Port and Host

```bash
# Bind to localhost only (more secure)
python run_http_server.py 8000 127.0.0.1

# Use different port
python run_http_server.py 3000 127.0.0.1
```

### Environment Variables

You can configure via environment variables:

```bash
export GOOGLE_MCP_CONFIG_PATH=/path/to/config.json
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
python run_http_server.py 8000
```

### Multiple Instances

Run multiple instances on different ports:

```bash
# Instance 1
python run_http_server.py 8000

# Instance 2 (different terminal)
python run_http_server.py 8001
```

Configure clients to connect to different instances as needed.

## Support

For issues and questions:
1. Check server logs
2. Review this documentation
3. Test with MCP Inspector
4. Open an issue in the repository
