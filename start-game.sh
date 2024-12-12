#!/bin/bash

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOGS_DIR="$PROJECT_ROOT/logs"

# Create logs directory if it doesn't exist
mkdir -p "$LOGS_DIR"

print_header() {
    echo -e "\n${BLUE}============================================${NC}"
    echo -e "${BLUE}       Dark Station Chronicles              ${NC}"
    echo -e "${BLUE}============================================${NC}\n"
}

check_environment() {
    echo -e "${YELLOW}Checking environment...${NC}"

    # Check for Python virtual environment
    if [ ! -d "$PROJECT_ROOT/venv" ]; then
        echo -e "${RED}Virtual environment not found! Please run setup.py first.${NC}"
        exit 1
    fi

    # Check for .env file
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        echo -e "${RED}No .env file found! Creating from template...${NC}"
        if [ -f "$PROJECT_ROOT/.env.template" ]; then
            cp "$PROJECT_ROOT/.env.template" "$PROJECT_ROOT/.env"
            echo -e "${YELLOW}Please edit .env file and add your API key!${NC}"
            exit 1
        else
            echo -e "${RED}No .env.template found! Please run setup.py first.${NC}"
            exit 1
        fi
    fi

    # Check for node_modules and install/update dependencies
    cd "$PROJECT_ROOT/frontend"
    if [ ! -d "node_modules" ] || [ ! -f "node_modules/.package-lock.json" ]; then
        echo -e "${YELLOW}Installing frontend dependencies...${NC}"
        npm install
        npm install react-markdown @tailwindcss/typography
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to install frontend dependencies!${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}Checking for new dependencies...${NC}"
        npm install react-markdown @tailwindcss/typography
    fi
}

start_servers() {
    # Activate virtual environment
    source "$PROJECT_ROOT/venv/bin/activate"

    # Start backend server
    echo -e "${GREEN}Starting backend server...${NC}"
    cd "$PROJECT_ROOT"
    python -m uvicorn src.api.main:app --reload --host 0.0.0.0 > "$LOGS_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!

    # Give the backend a moment to start
    sleep 2

    # Check if backend started successfully
    if ! curl -s http://localhost:8000 > /dev/null; then
        echo -e "${RED}Backend server failed to start! Check logs/backend.log${NC}"
        cleanup
        exit 1
    fi

    # Start frontend server
    echo -e "${GREEN}Starting frontend server...${NC}"
    cd "$PROJECT_ROOT/frontend"
    npm run dev > "$LOGS_DIR/frontend.log" 2>&1 &
    FRONTEND_PID=$!

    # Give the frontend a moment to start
    sleep 3

    # Check if frontend started successfully
    if ! curl -s http://localhost:5173 > /dev/null; then
        echo -e "${RED}Frontend server failed to start! Check logs/frontend.log${NC}"
        cleanup
        exit 1
    fi
}

open_game() {
    echo -e "${GREEN}Opening game in browser...${NC}"
    xdg-open http://localhost:5173
}

show_status() {
    echo -e "\n${GREEN}Game is running!${NC}"
    echo -e "${BLUE}Backend server: http://localhost:8000${NC}"
    echo -e "${BLUE}Frontend server: http://localhost:5173${NC}"
    echo -e "${YELLOW}Logs are being saved to:${NC}"
    echo -e "  Backend:  $LOGS_DIR/backend.log"
    echo -e "  Frontend: $LOGS_DIR/frontend.log"
    echo -e "\n${RED}Press Ctrl+C to stop all servers${NC}\n"
}

cleanup() {
    echo -e "\n${RED}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Main execution
print_header
check_environment
start_servers
open_game
show_status

# Register cleanup for different signals
trap cleanup SIGINT SIGTERM EXIT

# Wait for user interrupt
wait
