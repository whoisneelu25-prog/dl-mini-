#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
PYTHON_BIN="python3"
if [ -d "venv" ]; then
    source venv/bin/activate
    if [ -f "venv/bin/python3" ]; then
        PYTHON_BIN="venv/bin/python3"
    fi
fi
export PYTHONPATH="$DIR/ai_presentation_generator:$PYTHONPATH"
echo "Starting AI Presentation Generator Web Application on http://localhost:8000 ..."
exec "$PYTHON_BIN" ai_presentation_generator/server.py
