#!/bin/bash
# Script to run the backend server on port 5001

# Ensure we're in a Python virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Python virtual environment not active. Please activate your virtual environment first."
    echo "You can use: source venv/bin/activate"
    exit 1
fi

# Set the PORT environment variable
export PORT=5001

# Run the server script
python3 scripts/run_server.py

# Check exit status
if [ $? -ne 0 ]; then
    echo "Server failed to start."
    exit 1
fi 