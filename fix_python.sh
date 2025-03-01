#!/bin/bash

# Create a Python wrapper to unset problematic variables
cat > $HOME/.local/bin/python3-clean << 'EOF'
#!/bin/bash
# Unset problematic variables
unset PYTHONHOME
unset PYTHONPATH
# Run the real Python interpreter
exec /usr/bin/python3 "$@"
EOF

# Make it executable
chmod +x $HOME/.local/bin/python3-clean

# Create directory if it doesn't exist
mkdir -p $HOME/.local/bin

# Check if .local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> $HOME/.bashrc
    echo "Added ~/.local/bin to your PATH in .bashrc"
fi

# Create alias for python3 in bashrc if it doesn't exist
if ! grep -q "alias python3=" $HOME/.bashrc; then
    echo 'alias python3="python3-clean"' >> $HOME/.bashrc
    echo "Added python3 alias to your .bashrc"
fi

# Apply changes to current shell
export PATH="$HOME/.local/bin:$PATH"
alias python3="python3-clean"

echo "Python environment fixed!"
echo "The fix has been applied to your current shell and will persist for future sessions."
echo "You may need to restart Cursor for it to pick up the changes."
echo ""
echo "Try running 'python3 --version' to test." 