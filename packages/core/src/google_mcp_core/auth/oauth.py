from __future__ import annotations

import http.server
import socketserver
import webbrowser
import warnings
from typing import Optional
from urllib.parse import urlparse, parse_qs, urlencode

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import requests

from google_mcp_core.config import OAuthConfig
from google_mcp_core.auth.token_store import FileTokenStore, TokenStore


class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    """Custom handler to capture OAuth callback with custom path."""
    
    def do_GET(self):
        """Handle the OAuth callback."""
        # Parse the authorization code from the callback
        query = parse_qs(urlparse(self.path).query)
        
        if 'code' in query:
            self.server.auth_code = query['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Authentication successful!</h1><p>You can close this window.</p></body></html>')
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Authentication failed!</h1></body></html>')
    
    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


def get_oauth_credentials(
    config: OAuthConfig,
    scopes: list[str],
    token_store: Optional[TokenStore] = None,
) -> Credentials:
    store = token_store or FileTokenStore(config.token_store)
    credentials = store.read()
    if credentials and credentials.valid:
        return credentials
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        store.write(credentials)
        return credentials
    
    # Parse redirect URI
    parsed = urlparse(config.redirect_uri)
    port = parsed.port or 8080
    
    client_config = {
        "installed": {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "redirect_uris": [config.redirect_uri],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=scopes,
        redirect_uri=config.redirect_uri
    )
    
    # Generate authorization URL
    # prompt=consent forces Google to show consent screen and provide refresh_token
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    print(f"Please visit this URL to authorize this application: {auth_url}")
    webbrowser.open(auth_url)
    
    # Start local server to receive callback
    with socketserver.TCPServer(("", port), OAuthCallbackHandler) as httpd:
        httpd.auth_code = None
        httpd.handle_request()
        
        if not httpd.auth_code:
            raise Exception("Failed to receive authorization code")
        
        # Exchange authorization code for token manually to avoid oauthlib scope validation
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": httpd.auth_code,
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "redirect_uri": config.redirect_uri,
            "grant_type": "authorization_code",
        }
        
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        token_response = response.json()
        
        # Create credentials from token response
        credentials = Credentials(
            token=token_response["access_token"],
            refresh_token=token_response.get("refresh_token"),
            token_uri=token_url,
            client_id=config.client_id,
            client_secret=config.client_secret,
            scopes=token_response.get("scope", " ".join(scopes)).split()
        )
    
    store.write(credentials)
    return credentials
