#!/usr/bin/env python3
"""
Test script to validate Google Calendar MCP server setup.
Run this to verify everything is configured correctly.
"""

import sys
import json
import time
import subprocess
import urllib.request
import urllib.error
from pathlib import Path


def print_status(message, status="info"):
    """Print colored status messages."""
    colors = {
        "info": "\033[94m",      # Blue
        "success": "\033[92m",   # Green
        "warning": "\033[93m",   # Yellow
        "error": "\033[91m",     # Red
        "reset": "\033[0m"
    }
    color = colors.get(status, colors["info"])
    reset = colors["reset"]
    symbols = {
        "info": "ℹ",
        "success": "✓",
        "warning": "⚠",
        "error": "✗"
    }
    symbol = symbols.get(status, "•")
    print(f"{color}{symbol} {message}{reset}")


def check_dependencies():
    """Check if required dependencies are installed."""
    print_status("Checking dependencies...", "info")

    try:
        import google_calendar_mcp
        print_status("google-mcp-calendar package found", "success")
    except ImportError:
        print_status("google-mcp-calendar not installed", "error")
        print_status("Run: pip install -e .", "warning")
        return False

    try:
        import google_mcp_core
        print_status("google-mcp-core package found", "success")
    except ImportError:
        print_status("google-mcp-core not installed", "error")
        print_status("Install google-mcp-core first", "warning")
        return False

    try:
        import starlette
        print_status("starlette package found", "success")
    except ImportError:
        print_status("starlette not installed", "error")
        print_status("Run: pip install starlette", "warning")
        return False

    try:
        import uvicorn
        print_status("uvicorn package found", "success")
    except ImportError:
        print_status("uvicorn not installed", "error")
        print_status("Run: pip install uvicorn", "warning")
        return False

    return True


def check_oauth_config():
    """Check if OAuth configuration exists."""
    print_status("Checking OAuth configuration...", "info")

    # Common config locations
    config_paths = [
        Path.home() / ".config" / "google-mcp-core" / "credentials.json",
        Path("credentials.json"),
    ]

    for path in config_paths:
        if path.exists():
            print_status(f"OAuth credentials found at: {path}", "success")
            return True

    print_status("OAuth credentials not found", "warning")
    print_status("You'll need to configure OAuth on first run", "info")
    return None  # Not an error, just needs setup


def test_server_import():
    """Test if server module can be imported."""
    print_status("Testing server module import...", "info")

    try:
        from google_calendar_mcp import server
        print_status("Server module imported successfully", "success")
        return True
    except Exception as e:
        print_status(f"Failed to import server: {e}", "error")
        return False


def test_http_server_import():
    """Test if HTTP server module can be imported."""
    print_status("Testing HTTP server module import...", "info")

    try:
        from google_calendar_mcp import http_server
        print_status("HTTP server module imported successfully", "success")
        return True
    except Exception as e:
        print_status(f"Failed to import HTTP server: {e}", "error")
        return False


def start_test_server():
    """Start the HTTP server for testing."""
    print_status("Starting HTTP server on port 8888...", "info")

    try:
        # Start server in background
        process = subprocess.Popen(
            [sys.executable, "run_http_server.py", "8888", "127.0.0.1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait for server to start
        print_status("Waiting for server to initialize...", "info")
        time.sleep(3)

        # Check if process is still running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print_status("Server failed to start", "error")
            if stderr:
                print(f"\nError output:\n{stderr}")
            return None

        print_status("Server started (PID: {})".format(process.pid), "success")
        return process

    except Exception as e:
        print_status(f"Failed to start server: {e}", "error")
        return None


def test_health_endpoint(port=8888):
    """Test the health endpoint."""
    print_status("Testing health endpoint...", "info")

    try:
        url = f"http://127.0.0.1:{port}/health"
        response = urllib.request.urlopen(url, timeout=5)
        content = response.read().decode('utf-8')

        if content == "ok":
            print_status("Health endpoint responding correctly", "success")
            return True
        else:
            print_status(f"Unexpected health response: {content}", "warning")
            return False

    except urllib.error.URLError as e:
        print_status(f"Health endpoint not accessible: {e}", "error")
        return False
    except Exception as e:
        print_status(f"Error testing health endpoint: {e}", "error")
        return False


def test_mcp_endpoint(port=8888):
    """Test the MCP endpoint."""
    print_status("Testing MCP endpoint...", "info")

    try:
        url = f"http://127.0.0.1:{port}/mcp"

        # Try a simple GET first (SSE connection attempt)
        req = urllib.request.Request(url, method='GET')
        response = urllib.request.urlopen(req, timeout=5)

        print_status("MCP endpoint is accessible", "success")
        return True

    except urllib.error.HTTPError as e:
        # Some error codes might be expected for GET without proper headers
        if e.code in [400, 405]:
            print_status("MCP endpoint is accessible (expected error for test)", "success")
            return True
        else:
            print_status(f"MCP endpoint returned error: {e.code}", "warning")
            return False

    except Exception as e:
        print_status(f"Error testing MCP endpoint: {e}", "error")
        return False


def print_summary(results):
    """Print test summary."""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for r in results.values() if r is True)
    warned = sum(1 for r in results.values() if r is None)
    failed = sum(1 for r in results.values() if r is False)
    total = len(results)

    print(f"\nPassed: {passed}/{total}")
    if warned > 0:
        print(f"Warnings: {warned}")
    if failed > 0:
        print(f"Failed: {failed}")

    print("\n" + "="*60)

    if failed == 0:
        print_status("All critical tests passed! ✓", "success")
        print_status("Server is ready to use", "success")
        print("\nNext steps:")
        print("  1. Run: python run_http_server.py 8000")
        print("  2. Configure your MCP client")
        print("  3. See QUICKSTART.md for details")
    else:
        print_status("Some tests failed", "error")
        print_status("Please fix the issues above before using the server", "warning")

    print("="*60 + "\n")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Google Calendar MCP Server - Connection Test")
    print("="*60 + "\n")

    results = {}
    server_process = None

    try:
        # Run tests
        results["dependencies"] = check_dependencies()
        if not results["dependencies"]:
            print_summary(results)
            return 1

        results["oauth_config"] = check_oauth_config()
        results["server_import"] = test_server_import()
        results["http_server_import"] = test_http_server_import()

        # Only test server if imports work
        if results["server_import"] and results["http_server_import"]:
            server_process = start_test_server()

            if server_process:
                results["health_endpoint"] = test_health_endpoint()
                results["mcp_endpoint"] = test_mcp_endpoint()
            else:
                results["health_endpoint"] = False
                results["mcp_endpoint"] = False

        # Print summary
        print_summary(results)

        # Return appropriate exit code
        if any(r is False for r in results.values()):
            return 1
        return 0

    except KeyboardInterrupt:
        print_status("\nTest interrupted by user", "warning")
        return 1

    finally:
        # Clean up server process
        if server_process and server_process.poll() is None:
            print_status("Stopping test server...", "info")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
                print_status("Test server stopped", "success")
            except subprocess.TimeoutExpired:
                server_process.kill()
                print_status("Test server forcefully stopped", "warning")


if __name__ == "__main__":
    sys.exit(main())
