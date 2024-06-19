#!/bin/bash

# Check if the first command-line argument is "--files"
if [ "$1" == "--files" ]; then
    # Run autopep8 in diff mode to show files that would be modified
    python -m autopep8 --diff --recursive . | grep -E '^--- original/\.' | sed 's/--- original\/\.//; s/\\//'
# Check if the first command-line argument is "--format"
elif [ "$1" == "--format" ]; then
    # Run autopep8 in place to format files
    python -m autopep8 --in-place --recursive .
elif [ "$1" == "--flake8" ]; then
    python -m flake8
elif [ "$1" == "--mypy" ]; then
    python -m mypy src
    python -m mypy tests
else
    python -m flake8
    python -m mypy src
    python -m mypy tests
fi