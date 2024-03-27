#!/bin/bash

# Loop through each subdirectory in src and run unittest discovery
for dir in src/*; do
    if [ -d "$dir/tests" ]; then
        echo "Running tests in $dir"
        python -m unittest discover -s "$dir" -p "test*.py"
    fi
done
