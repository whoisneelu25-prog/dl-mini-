#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
if [ -d "venv" ]; then
    source venv/bin/activate
fi
export PYTHONPATH="$DIR/ai_presentation_generator:$PYTHONPATH"
echo "Starting AI Presentation Generator Web Application on http://localhost:8000 ..."
python3 ai_presentation_generator/server.py
