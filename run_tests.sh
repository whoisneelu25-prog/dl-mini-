#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
if [ -d "venv" ]; then
    source venv/bin/activate
fi
export PYTHONPATH="$DIR/ai_presentation_generator:$PYTHONPATH"
echo "Executing pytest test suite (58 tests)..."
pytest ai_presentation_generator/tests/ -v
