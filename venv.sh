#!/bin/bash

# Clean up potentially problematic environment variables
unset PYTHONHOME
unset PYTHONPATH

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Install requirements if needed
if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    source .venv/bin/activate
    pip install -r requirements.txt
    deactivate
fi

# Activate the virtual environment and provide instructions
source .venv/bin/activate
echo ""
echo "Virtual environment activated with clean Python settings."
echo "Your environment is now set up correctly."
echo ""
echo "Use the following commands in this shell:"
echo "- 'python3' to run the Python interpreter"
echo "- 'python3 backend/app.py' to run the backend app"
echo "- 'pytest tests/' to run tests"
echo ""
echo "When you're done, type 'deactivate' to exit the virtual environment."
echo ""
exec $SHELL 