#!/bin/bash
# Launch script for METAR to IWXXM Backend API (Bash/Linux/macOS)
# Usage: ./launch_api.sh [--port PORT] [--host HOST] [--reload]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$REPO_ROOT/.venv"

# Default values
HOST="0.0.0.0"
PORT="8001"
RELOAD=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --reload)
            RELOAD="--reload"
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Launch the METAR to IWXXM Backend API server"
            echo ""
            echo "Options:"
            echo "  --port PORT     Port to listen on (default: 8001)"
            echo "  --host HOST     Host to bind to (default: 0.0.0.0)"
            echo "  --reload        Enable auto-reload on code changes"
            echo "  --help          Show this help message"
            echo ""
            echo "Example:"
            echo "  $0 --port 8001 --reload"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

cd "$REPO_ROOT"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at $VENV_DIR"
    echo ""
    echo "Please create it first:"
    echo "  python -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install fastapi uvicorn tpg python-multipart"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Check if dependencies are installed
if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "❌ Required dependencies not found"
    echo ""
    echo "Installing dependencies..."
    pip install fastapi uvicorn tpg python-multipart
fi

# Launch the backend API
echo "🚀 Starting METAR to IWXXM Backend API..."
echo "📡 Server: http://$HOST:$PORT"
echo "📚 API Docs: http://localhost:$PORT/docs"
echo "📖 ReDoc: http://localhost:$PORT/redoc"
echo "💚 Health: http://localhost:$PORT/health"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

python -m uvicorn backend.api:app --host "$HOST" --port "$PORT" $RELOAD
