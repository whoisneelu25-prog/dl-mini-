#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
STREAMLIT_BIN="streamlit"
if [ -d "venv" ]; then
    source venv/bin/activate
    if [ -f "venv/bin/streamlit" ]; then
        STREAMLIT_BIN="venv/bin/streamlit"
    fi
fi
export PYTHONPATH="$DIR/ai_presentation_generator:$PYTHONPATH"
echo "Starting AI Presentation Generator Streamlit on http://localhost:8501 ..."
exec "$STREAMLIT_BIN" run ai_presentation_generator/app.py
