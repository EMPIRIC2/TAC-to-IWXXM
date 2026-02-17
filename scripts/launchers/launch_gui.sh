#!/bin/bash
# Launch script for METAR to IWXXM Converter Frontend (Bash/Linux/macOS)
# Usage: ./launch_gui.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$REPO_ROOT/frontend"

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "[ERROR] Frontend directory not found at: $FRONTEND_DIR"
    echo "[INFO] Please ensure the frontend submodule is initialized:"
    echo "[INFO]   git submodule update --init --recursive"
    exit 1
fi

# Parse arguments (for future extensibility)
while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            echo "Usage: $0"
            echo ""
            echo "This script launches the React/Vite frontend development server."
            echo "No arguments required - Vite uses default port 5173."
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

# Launch the frontend dev server
echo ""
echo "========================================"
echo " METAR to IWXXM Converter Frontend"
echo "========================================"
echo " Server will start at http://localhost:5173"
echo " (Vite default port)"
echo "========================================"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

npm run dev


python -m uvicorn gui.app:app --host "$HOST" --port "$PORT" $RELOAD
