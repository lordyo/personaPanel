#!/bin/bash

# Clean up potentially problematic environment variables
unset PYTHONHOME
unset PYTHONPATH

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install requirements if needed
if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

# Run pytest with any provided arguments
if [ "$#" -ge 1 ]; then
    python3 -m pytest "$@" -v
else
    echo "Running all tests..."
    python3 -m pytest -v
fi

# Deactivate virtual environment
deactivate 