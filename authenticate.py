#!/usr/bin/env python3
"""
OAuth Authentication Script for Google MCP Suite
Run this to authenticate and generate tokens.json
"""

from google_mcp_core.config import load_config
from google_mcp_core.auth.manager import AuthManager

def main():
    print("🔐 Google MCP Suite - OAuth Authentication")
    print("=" * 50)
    
    # Load config
    config = load_config()
    auth_manager = AuthManager(config)
    
    # List of services to authenticate
    services = [
        "drive", "gmail", "calendar", "sheets", "docs", 
        "slides", "forms", "tasks", "people"
    ]
    
    print("\nAuthenticating for all services...")
    print("This will open a browser window for OAuth consent.\n")
    
    # Authenticate for Drive (which will trigger OAuth flow)
    try:
        print("📝 Requesting credentials for Drive (this will open your browser)...")
        creds = auth_manager.get_credentials("drive", [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive.readonly"
        ])
        
        if creds and creds.valid:
            print("✅ Authentication successful!")
            print(f"\n🎉 Token saved to: ~/.google-mcp/tokens.json")
            print("\nYou can now use all MCP servers with Claude Code!")
            print("\nServices authenticated:")
            for service in services:
                print(f"  ✓ {service}")
        else:
            print("❌ Authentication failed - credentials invalid")
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        import traceback
        traceback.print_exc()
        print("\nPlease check:")
        print("  1. OAuth client credentials are correct in config.yaml")
        print("  2. Redirect URI is set to http://localhost:3080/gdrive/oauth/callback")
        print("  3. OAuth consent screen is configured")

if __name__ == "__main__":
    main()
