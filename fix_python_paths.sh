#!/bin/bash

# Script to check and fix Python path issues on Debian

echo "========== Python Path Fix Script =========="
echo "This script will check and fix Python path issues without reinstalling"
echo

# Check current Python installations
echo "Current Python installations:"
which python python3 || echo "Python not found in PATH"
python3 --version 2>/dev/null || echo "Python3 not working properly"
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

# Check if Python works properly
echo "Testing Python functionality with clean environment:"
env -u PYTHONHOME -u PYTHONPATH python3 --version
if [ $? -eq 0 ]; then
    echo "✅ Python works with clean environment"
else
    echo "❌ Python still has issues even with clean environment"
    echo "   You may need to run the full reinstall_python.sh script"
fi
echo

# Backup .bashrc
echo "Creating backup of .bashrc..."
cp ~/.bashrc ~/.bashrc.bak
echo "Backup created at ~/.bashrc.bak"
echo

# Clean up any conflicting environment variables in .bashrc
echo "Cleaning up any Python environment variables in .bashrc..."
sed -i '/PYTHONHOME=/d' ~/.bashrc
sed -i '/PYTHONPATH=/d' ~/.bashrc
sed -i '/alias python3=/d' ~/.bashrc

# Add clean environment aliases
echo "Setting up clean Python aliases..."
echo '# Clean Python environment aliases' >> ~/.bashrc
echo 'alias python3="env -u PYTHONHOME -u PYTHONPATH python3"' >> ~/.bashrc
echo 'alias pip3="env -u PYTHONHOME -u PYTHONPATH pip3"' >> ~/.bashrc
echo 'alias python="python3"' >> ~/.bashrc
echo 'alias pip="pip3"' >> ~/.bashrc

# Create a clean Python wrapper script in ~/.local/bin
echo "Creating Python wrapper script..."
mkdir -p ~/.local/bin

cat > ~/.local/bin/python3-clean << 'EOF'
#!/bin/bash
# Unset problematic variables
unset PYTHONHOME
unset PYTHONPATH
# Run the real Python interpreter
exec /usr/bin/python3 "$@"
EOF

chmod +x ~/.local/bin/python3-clean

# Add ~/.local/bin to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo "Added ~/.local/bin to your PATH in .bashrc"
fi

# Create symlink for python
ln -sf ~/.local/bin/python3-clean ~/.local/bin/python-clean

# Test the wrapper
echo "Testing Python wrapper script:"
~/.local/bin/python3-clean -c "import sys; print('Python wrapper works! Path:', sys.path[:3])"
echo

# Create a simple script to fix cursor environment
cat > ./cursor_fix.sh << 'EOF'
#!/bin/bash
# To fix Python in Cursor, run this in your terminal before launching Cursor:
unset PYTHONHOME PYTHONPATH
cursor
EOF
chmod +x ./cursor_fix.sh

echo "========== Path Fix Complete =========="
echo "Python paths have been fixed."
echo 
echo "To use Python with a clean environment:"
echo "  1. In current terminal: source ~/.bashrc"
echo "  2. Then use python3/pip3 normally"
echo
echo "If you're having issues with Cursor specifically:"
echo "  1. Close Cursor"
echo "  2. Run ./cursor_fix.sh to launch Cursor with clean environment"
echo
echo "For your project, continue using your wrapper scripts:"
echo "  ./run-app                    # To run your backend app"
echo "  ./run-tests                  # To run your tests" 
echo "  ./py <args>                  # To run other Python commands"
echo "===========================================" 