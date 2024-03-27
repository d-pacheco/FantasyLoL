#!/bin/bash

echo "auth tests"
python -m unittest discover -s auth -p "test*.py"
echo "common tests"
python -m unittest discover -s common -p "test*.py"
echo "db tests"
python -m unittest discover -s db -p "test*.py"
echo "fantasy tests"
python -m unittest discover -s fantasy -p "test*.py"
echo "riot tests"
python -m unittest discover -s riot -p "test*.py"