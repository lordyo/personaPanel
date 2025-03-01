#!/bin/bash

# setup_python_env.sh
# Sets up a clean Python environment with a virtual environment for this project

set -e  # Exit on error

# Print section header
print_header() {
    echo
    echo "=================================================="
    echo "  $1"
    echo "=================================================="
}

# Ensure we're in the project root directory
cd "$(dirname "$0")"
PROJECT_DIR="$(pwd)"

print_header "CHECKING PYTHON INSTALLATION"
echo "Python version:"
env -u PYTHONHOME -u PYTHONPATH python3 --version

# Check if virtual environment exists
VENV_DIR="$PROJECT_DIR/venv"
if [ -d "$VENV_DIR" ]; then
    print_header "EXISTING VIRTUAL ENVIRONMENT FOUND"
    echo "An existing virtual environment was found at:"
    echo "$VENV_DIR"
    
    read -p "Do you want to remove it and create a new one? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    else
        echo "Using existing virtual environment."
        source "$VENV_DIR/bin/activate"
        print_header "VIRTUAL ENVIRONMENT ACTIVATED"
        echo "Python version in virtual environment:"
        python3 --version
        print_header "SETUP COMPLETE"
        echo "Your Python environment is ready!"
        echo "To activate the virtual environment, run:"
        echo "  source venv/bin/activate"
        exit 0
    fi
fi

print_header "CREATING VIRTUAL ENVIRONMENT"
echo "Creating a new virtual environment in: $VENV_DIR"
env -u PYTHONHOME -u PYTHONPATH python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

print_header "INSTALLING DEPENDENCIES"
# Upgrade pip first
python3 -m pip install --upgrade pip

# Check if requirements.txt exists
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    echo "Installing packages from requirements.txt..."
    python3 -m pip install -r "$PROJECT_DIR/requirements.txt"
else
    echo "No requirements.txt found."
    echo "Installing common development packages..."
    python3 -m pip install pytest flask
fi

print_header "CREATING HELPER SCRIPTS"

# Create a simple activation script
cat > "$PROJECT_DIR/activate-env" << 'EOF'
#!/bin/bash
# Helper script to activate the virtual environment
source "$(dirname "$0")/venv/bin/activate"
echo "Python virtual environment activated!"
echo "Type 'deactivate' to exit the virtual environment."
EOF
chmod +x "$PROJECT_DIR/activate-env"

# Create a run-app script if not exists
if [ ! -f "$PROJECT_DIR/run-app" ]; then
    cat > "$PROJECT_DIR/run-app" << 'EOF'
#!/bin/bash
# Run the application with the virtual environment
SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/venv/bin/activate"
echo "Starting application..."
python3 backend/app.py
EOF
    chmod +x "$PROJECT_DIR/run-app"
fi

# Create a run-tests script if not exists
if [ ! -f "$PROJECT_DIR/run-tests" ]; then
    cat > "$PROJECT_DIR/run-tests" << 'EOF'
#!/bin/bash
# Run tests with the virtual environment
SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/venv/bin/activate"
echo "Running tests..."
python3 -m pytest "$@"
EOF
    chmod +x "$PROJECT_DIR/run-tests"
fi

print_header "CHECKING INSTALLATION"
echo "Python version in virtual environment:"
python3 --version
echo
echo "Installed packages:"
python3 -m pip list

print_header "SETUP COMPLETE"
echo "Your Python environment is ready!"
echo
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo "  # or use the helper script"
echo "  ./activate-env"
echo
echo "To run your application:"
echo "  ./run-app"
echo
echo "To run tests:"
echo "  ./run-tests"
echo
echo "Happy coding!" 