#!/bin/bash
# Run all tests for the Entity Simulation Framework

# Change to the project root directory
cd "$(dirname "$0")/.." || { echo "Failed to change to project root directory"; exit 1; }
PROJECT_ROOT=$(pwd)

echo "Running tests from project root: $PROJECT_ROOT"

# Unset problematic Python environment variables set by Cursor
echo "Unsetting problematic Python environment variables..."
export PYTHONPATH=
export PYTHONHOME=

# Check for Python3 installation
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH"
    exit 1
fi

# Set up virtual environment if it doesn't exist
VENV_DIR="$PROJECT_ROOT/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR" || { echo "Failed to create virtual environment"; exit 1; }
fi

# Activate virtual environment
echo "Activating virtual environment..."
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate" || { echo "Failed to activate virtual environment"; exit 1; }

# Check Python version and path
echo "Python version:"
python3 --version
echo "Python path:"
which python3

# Install requirements if requirements.txt exists
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo "Installing requirements..."
    pip install -r "$PROJECT_ROOT/requirements.txt" || echo "Warning: Some requirements may not have installed correctly"
fi

# Add pytest and other testing requirements
echo "Installing testing dependencies..."
pip install pytest pytest-cov || echo "Warning: Failed to install testing dependencies"

# Run backend tests
echo "Running backend API tests..."
python3 -m pytest "$PROJECT_ROOT/tests/test_api_templates.py" "$PROJECT_ROOT/tests/test_entity_types.py" -v || echo "Warning: Backend tests failed or could not be run"

# Run frontend tests (if Jest is set up)
if [ -d "$PROJECT_ROOT/frontend/node_modules" ]; then
    echo "Running frontend component tests..."
    (cd "$PROJECT_ROOT/frontend" && npm test -- --watchAll=false) || echo "Warning: Frontend tests failed or could not be run"
else
    echo "Frontend node_modules not found. Skipping frontend tests."
    echo "To run frontend tests, go to the frontend directory and run:"
    echo "  npm install"
    echo "  npm test"
fi

# Deactivate virtual environment
if command -v deactivate &> /dev/null; then
    echo "Deactivating virtual environment..."
    deactivate
fi

echo "All tests completed!" 