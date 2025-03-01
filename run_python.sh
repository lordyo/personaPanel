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

# Run the specified Python script with arguments
if [ "$#" -ge 1 ]; then
    python3 "$@"
else
    echo "Usage: ./run_python.sh <script.py> [arguments]"
    echo "Example: ./run_python.sh backend/app.py"
fi

# Deactivate virtual environment
deactivate 