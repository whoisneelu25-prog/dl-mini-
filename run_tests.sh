#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
PYTEST_BIN="pytest"
if [ -d "venv" ]; then
    source venv/bin/activate
    if [ -f "venv/bin/pytest" ]; then
        PYTEST_BIN="venv/bin/pytest"
    fi
fi
export PYTHONPATH="$DIR/ai_presentation_generator:$PYTHONPATH"
echo "Executing pytest test suite (58 tests)..."
exec "$PYTEST_BIN" ai_presentation_generator/tests/ -v
