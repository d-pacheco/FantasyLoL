#!/bin/bash

source "$(dirname "$0")/find_python.sh"

echo "Running tests"
$PYTHON -m unittest discover -s tests -p "test*.py"
