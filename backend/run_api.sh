#!/bin/bash
# Quick script to run the Entity Simulation Framework API server

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

# Run the server
echo "Starting API server..."
python3 scripts/run_server.py

# Deactivate venv when done
deactivate 