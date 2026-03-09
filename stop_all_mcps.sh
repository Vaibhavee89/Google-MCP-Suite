#!/bin/bash

# Stop All Google MCP Servers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${RED}Stopping Google MCP Suite Servers${NC}"
echo "=================================="

# Base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="$BASE_DIR/.pids"

if [ ! -d "$PID_DIR" ]; then
    echo -e "${YELLOW}No PID directory found. Servers may not be running.${NC}"
    exit 0
fi

# Stop all servers
for pid_file in "$PID_DIR"/*.pid; do
    if [ -f "$pid_file" ]; then
        package=$(basename "$pid_file" .pid)
        pid=$(cat "$pid_file")

        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${GREEN}Stopping $package (PID: $pid)${NC}"
            kill $pid
            sleep 1

            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                echo -e "${YELLOW}  Force stopping...${NC}"
                kill -9 $pid 2>/dev/null || true
            fi

            echo -e "  ${GREEN}✓${NC} Stopped"
        else
            echo -e "${YELLOW}$package already stopped${NC}"
        fi

        rm "$pid_file"
    fi
done

echo ""
echo -e "${GREEN}All servers stopped!${NC}"
