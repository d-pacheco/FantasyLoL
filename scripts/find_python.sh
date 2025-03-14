#!/bin/bash

# Find Python interpreter (prioritizing python3.12)
PYTHON=$(command -v python3.12 || command -v python)

# Ensure Python is available
if [ -z "$PYTHON" ]; then
    echo "Error: Python is not installed or not in PATH." >&2
    exit 1
fi

# Export the PYTHON variable so it can be used in other scripts
export PYTHON
