#!/bin/bash

source "$(dirname "$0")/find_python.sh"

# Ensure required tools are installed
for tool in autopep8 flake8 mypy; do
    if ! $PYTHON -m pip show "$tool" > /dev/null 2>&1; then
        echo "Error: $tool is not installed. Install it using: $PYTHON -m pip install $tool" >&2
        exit 1
    fi
done

# Check command-line argument
case "$1" in
    "--files")
        # Run autopep8 in diff mode to show files that would be modified
        $PYTHON -m autopep8 --diff --recursive . | grep -E '^--- original/\.' | sed 's/--- original\/\.//; s/\\//'
        ;;
    "--format")
        # Run autopep8 in place to format files
        $PYTHON -m autopep8 --in-place --recursive .
        ;;
    "--flake8")
        $PYTHON -m flake8
        ;;
    "--mypy")
        $PYTHON -m mypy src
        $PYTHON -m mypy tests
        ;;
    *)
        $PYTHON -m flake8
        $PYTHON -m mypy src
        $PYTHON -m mypy tests
        ;;
esac
