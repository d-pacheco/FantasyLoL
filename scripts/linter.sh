#!/bin/bash

# Check if the first command-line argument is "--files"
if [ "$1" == "--files" ]; then
    # Run autopep8 in diff mode to show files that would be modified
    python -m autopep8 --diff --recursive . | grep -E '^--- original/\.' | sed 's/--- original\/\.//; s/\\//'
# Check if the first command-line argument is "--format"
elif [ "$1" == "--format" ]; then
    # Run autopep8 in place to format files
    python -m autopep8 --in-place --recursive .
# Default case: run flake8 for static code analysis
else
    python -m flake8
fi