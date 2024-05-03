#!/bin/bash

# Run unittest discovery for tests in the tests directory
echo "Running tests"
python -m unittest discover -s tests -p "test*.py"
