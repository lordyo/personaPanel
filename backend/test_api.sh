#!/bin/bash
# Quick script to test the Entity Simulation Framework API

# Make sure we're in the backend directory
cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install -r ../requirements.txt
else
    source venv/bin/activate
fi

# Run the test script
echo "Running API tests..."
python3 scripts/test_api.py

# Get the exit code
EXIT_CODE=$?

# Deactivate venv
deactivate

# Exit with the test script's exit code
exit $EXIT_CODE 