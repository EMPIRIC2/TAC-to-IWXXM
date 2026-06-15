#!/bin/bash
# Start backend server with authentication disabled for development

cd "$(dirname "$0")"
export DISABLE_AUTH=true

echo "Starting backend server with DISABLE_AUTH=$DISABLE_AUTH"
.venv/bin/python -m uvicorn src.api:app --host 0.0.0.0 --port 8002 --reload
