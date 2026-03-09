#!/bin/bash

# Check Status of All Google MCP Servers

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Google MCP Suite Server Status${NC}"
echo "==============================="
echo ""

# Array of servers with their ports and names
declare -A SERVERS=(
    ["8001"]="Gmail"
    ["8002"]="Google Drive"
    ["8003"]="Calendar"
    ["8004"]="Sheets"
    ["8005"]="Docs"
    ["8006"]="Slides"
    ["8007"]="GCS"
    ["8008"]="Meet"
    ["8009"]="Admin SDK"
    ["8010"]="Chat"
    ["8011"]="Forms"
    ["8012"]="People"
    ["8013"]="Tasks"
    ["8014"]="BigQuery"
    ["8015"]="Cloud Logging"
    ["8016"]="Cloud Run"
    ["8017"]="Pub/Sub"
    ["8018"]="Vertex AI"
)

# Check each server
for port in $(echo "${!SERVERS[@]}" | tr ' ' '\n' | sort -n); do
    name="${SERVERS[$port]}"

    # Check if port is in use
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        # Try to hit the health endpoint
        if curl -s -f "http://localhost:$port/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} $name (port $port) - ${GREEN}Running${NC}"
        else
            echo -e "${YELLOW}⚠${NC} $name (port $port) - ${YELLOW}Port open but health check failed${NC}"
        fi
    else
        echo -e "${RED}✗${NC} $name (port $port) - ${RED}Not running${NC}"
    fi
done

echo ""
echo "To start all servers: ./start_all_mcps.sh"
echo "To stop all servers:  ./stop_all_mcps.sh"
