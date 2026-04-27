#!/bin/bash

source "$(dirname "$0")/find_python.sh"

# Ensure required tools are installed
for tool in ruff mypy; do
    if ! $PYTHON -m pip show "$tool" > /dev/null 2>&1; then
        echo "Error: $tool is not installed. Install it using: pip install \".[dev]\"" >&2
        exit 1
    fi
done

# Check command-line argument
case "$1" in
    "--files")
        # Show files that would be reformatted
        $PYTHON -m ruff format --diff .
        ;;
    "--format")
        # Format files in place
        $PYTHON -m ruff format .
        ;;
    "--lint")
        $PYTHON -m ruff check .
        ;;
    "--mypy")
        $PYTHON -m mypy src
        $PYTHON -m mypy tests
        ;;
    *)
        $PYTHON -m ruff check .
        $PYTHON -m ruff format --check .
        $PYTHON -m mypy src
        $PYTHON -m mypy tests
        ;;
esac
