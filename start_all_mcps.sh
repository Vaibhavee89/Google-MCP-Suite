#!/bin/bash

# Start All Google MCP Servers
# This script starts all MCP servers on their designated ports

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Google MCP Suite Servers${NC}"
echo "=================================="

# Base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Array of servers with their ports and package names
declare -A SERVERS=(
    ["8001"]="mcp-gmail"
    ["8002"]="mcp-google-drive"
    ["8003"]="mcp-calendar"
    ["8004"]="mcp-sheets"
    ["8005"]="mcp-docs"
    ["8006"]="mcp-slides"
    ["8007"]="mcp-gcs"
    ["8008"]="mcp-meet"
    ["8009"]="mcp-admin-sdk"
    ["8010"]="mcp-chat"
    ["8011"]="mcp-forms"
    ["8012"]="mcp-people"
    ["8013"]="mcp-tasks"
    ["8014"]="mcp-bigquery"
    ["8015"]="mcp-cloudlogging"
    ["8016"]="mcp-cloudrun"
    ["8017"]="mcp-pubsub"
    ["8018"]="mcp-vertexai"
)

# PID file directory
PID_DIR="$BASE_DIR/.pids"
mkdir -p "$PID_DIR"

# Function to start a server
start_server() {
    local port=$1
    local package=$2
    local package_dir="$BASE_DIR/packages/$package"

    # Check if port is already in use
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}Port $port already in use (${package})${NC}"
        return
    fi

    # Check if package directory exists
    if [ ! -d "$package_dir" ]; then
        echo -e "${RED}Package directory not found: $package_dir${NC}"
        return
    fi

    # Check if run_http_server.py exists
    if [ ! -f "$package_dir/run_http_server.py" ]; then
        echo -e "${YELLOW}Skipping $package (no run_http_server.py)${NC}"
        return
    fi

    echo -e "${GREEN}Starting $package on port $port${NC}"

    # Start the server in the background
    cd "$package_dir"
    nohup python run_http_server.py $port > "$PID_DIR/${package}.log" 2>&1 &
    local pid=$!
    echo $pid > "$PID_DIR/${package}.pid"

    # Wait a moment and check if it's still running
    sleep 1
    if ps -p $pid > /dev/null; then
        echo -e "  ${GREEN}✓${NC} Started (PID: $pid)"
    else
        echo -e "  ${RED}✗${NC} Failed to start (check $PID_DIR/${package}.log)"
    fi

    cd "$BASE_DIR"
}

# Start all servers
for port in $(echo "${!SERVERS[@]}" | tr ' ' '\n' | sort -n); do
    package="${SERVERS[$port]}"
    start_server $port $package
done

echo ""
echo -e "${GREEN}All servers started!${NC}"
echo ""
echo "To check status of all servers:"
echo "  ./check_mcps.sh"
echo ""
echo "To stop all servers:"
echo "  ./stop_all_mcps.sh"
echo ""
echo "Logs are available in: $PID_DIR/*.log"
