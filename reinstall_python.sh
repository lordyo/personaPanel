#!/bin/bash

# Script to reinstall Python and fix path issues on Debian

echo "========== Python Installation Script =========="
echo "This script will check and reinstall Python on your Debian system"
echo

# Check current Python installations
echo "Current Python installations:"
which python python3 || echo "Python not found in PATH"
echo

# Check for problematic environment variables
echo "Checking environment variables:"
if [ -n "$PYTHONHOME" ]; then
    echo "⚠️ PYTHONHOME is set to: $PYTHONHOME (This may cause issues)"
else
    echo "✅ PYTHONHOME is not set (good)"
fi

if [ -n "$PYTHONPATH" ]; then
    echo "⚠️ PYTHONPATH is set to: $PYTHONPATH (This may cause issues)"
else
    echo "✅ PYTHONPATH is not set (good)"
fi
echo

# Backup .bashrc
echo "Creating backup of .bashrc..."
cp ~/.bashrc ~/.bashrc.bak
echo "Backup created at ~/.bashrc.bak"
echo

# Update package listings
echo "Updating package listings..."
sudo apt update
echo

# Install Python development packages
echo "Installing Python and development packages..."
sudo apt install -y python3 python3-dev python3-venv python3-pip
echo

# Clean up any conflicting environment variables in .bashrc
echo "Cleaning up any Python environment variables in .bashrc..."
sed -i '/PYTHONHOME=/d' ~/.bashrc
sed -i '/PYTHONPATH=/d' ~/.bashrc
sed -i '/alias python3=/d' ~/.bashrc

# Add clean environment alias
echo "Setting up clean Python alias..."
echo '# Clean Python environment alias' >> ~/.bashrc
echo 'alias python-clean="env -u PYTHONHOME -u PYTHONPATH python3"' >> ~/.bashrc
echo 'alias pip-clean="env -u PYTHONHOME -u PYTHONPATH pip3"' >> ~/.bashrc
echo

# Install additional useful packages
echo "Installing additional Python packages..."
env -u PYTHONHOME -u PYTHONPATH pip3 install --user --upgrade pip setuptools wheel
echo

# Verify installation
echo "Verifying Python installation:"
env -u PYTHONHOME -u PYTHONPATH python3 --version
env -u PYTHONHOME -u PYTHONPATH pip3 --version
echo

# Test importing a standard library
echo "Testing Python standard library imports:"
env -u PYTHONHOME -u PYTHONPATH python3 -c "import sys; print('Python path:', sys.path[:3])"
env -u PYTHONHOME -u PYTHONPATH python3 -c "import os, json, encodings; print('Successfully imported standard libraries')"
echo

echo "========== Installation Complete =========="
echo "Python has been reinstalled and configured."
echo
echo "To use Python with a clean environment, use:"
echo "  python-clean                 # Instead of python3"
echo "  pip-clean                    # Instead of pip3"
echo
echo "For venv-based projects, continue using your wrapper scripts:"
echo "  ./run-app                    # To run your backend app"
echo "  ./run-tests                  # To run your tests"
echo "  ./py <args>                  # To run other Python commands"
echo
echo "You need to restart your terminal or run 'source ~/.bashrc' for"
echo "the changes to take effect in this session."
echo "==========================================" 