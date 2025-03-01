#!/bin/bash

# Add the alias to .bashrc if it doesn't exist already
if ! grep -q "alias python3='env -u PYTHONHOME -u PYTHONPATH python3'" $HOME/.bashrc; then
    echo "# Fix Python environment issues in Cursor" >> $HOME/.bashrc
    echo "alias python3='env -u PYTHONHOME -u PYTHONPATH python3'" >> $HOME/.bashrc
    echo "Added python3 alias to your .bashrc"
fi

# Apply the alias to the current shell
alias python3='env -u PYTHONHOME -u PYTHONPATH python3'

echo "Python environment fixed!"
echo "The fix has been applied to your current shell and will persist for future sessions."
echo "You may need to restart Cursor for it to pick up the changes."
echo ""
echo "Try running 'python3 --version' to test." 