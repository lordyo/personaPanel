#!/bin/bash
# py - Clean Python runner script for Cursor
#
# This script runs Python with clean environment variables
# to avoid issues with Cursor's environment.
#
# Usage:
#   ./py                      # Start a Python REPL
#   ./py script.py            # Run a Python script
#   ./py -m module            # Run a Python module
#   ./py -c "print('hello')"  # Run a Python command

# Check if we have a virtual environment, if so use it
SCRIPT_DIR="$(dirname "$0")"
VENV_DIR="$SCRIPT_DIR/venv"

if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/python" ]; then
    # Using virtual environment
    echo "Using Python from virtual environment"
    # Unset problematic environment variables and run Python from venv
    env -u PYTHONHOME -u PYTHONPATH "$VENV_DIR/bin/python" "$@"
else
    # Using system Python
    echo "Using system Python (no virtual environment found)"
    # Unset problematic environment variables and run system Python
    env -u PYTHONHOME -u PYTHONPATH python3 "$@"
fi 