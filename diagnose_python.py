#!/usr/bin/env python3
"""
Python Diagnostic Tool

This script helps diagnose Python configuration issues by checking:
- Python version and executable path
- Environment variables
- Python module search paths
- Import functionality for common modules
- Virtual environment status
- Cursor-specific environment issues
"""

import sys
import os
import site
import subprocess
from importlib import import_module
from importlib.util import find_spec

def print_section(title):
    """Print a section header with the given title."""
    print("\n" + "=" * 50)
    print(f"{title.center(50, '=')}")
    print("=" * 50)

def print_env_var(name):
    """Print the value of an environment variable if it exists."""
    value = os.environ.get(name)
    if value:
        print(f"{name}: {value}")
    else:
        print(f"{name}: Not set")

def main():
    """Run diagnostic checks and print results."""
    print_section("PYTHON DIAGNOSTIC INFORMATION")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Platform: {sys.platform}")

    print_section("ENVIRONMENT VARIABLES")
    print_env_var("PYTHONHOME")
    print_env_var("PYTHONPATH")
    print_env_var("PATH")

    print_section("PYTHON PATHS")
    print("sys.path:")
    for i, path in enumerate(sys.path):
        print(f"   {i}: {path}")
    
    print("\nsite.getsitepackages():")
    try:
        for path in site.getsitepackages():
            print(f"  - {path}")
    except Exception as e:
        print(f"  Error getting site packages: {e}")

    print_section("IMPORT TESTS")
    modules_to_test = [
        "encodings", "os", "sys", "json", "importlib",
        "flask", "pytest", "pip"
    ]

    for module in modules_to_test:
        try:
            import_module(module)
            print(f"✅ Successfully imported {module}")
        except ImportError as e:
            print(f"❌ Failed to import {module}: {e}")

    print_section("VIRTUAL ENVIRONMENT")
    if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        print(f"✅ Running in a virtual environment: {sys.prefix}")
        print(f"Base prefix: {sys.base_prefix}")
    else:
        print("❌ Not running in a virtual environment")

    print_section("CURSOR ENVIRONMENT")
    
    # Check if any Cursor paths in sys.path
    cursor_paths = [p for p in sys.path if "cursor" in p.lower()]
    if cursor_paths:
        print("❌ Found Cursor-related paths in sys.path:")
        for path in cursor_paths:
            print(f"  - {path}")
    else:
        print("✅ No Cursor-related paths found in sys.path")
    
    # Check PYTHONPATH for Cursor paths
    pythonpath = os.environ.get("PYTHONPATH", "")
    if pythonpath and "cursor" in pythonpath.lower():
        print("❌ Found Cursor in PYTHONPATH:")
        print(f"  {pythonpath}")
    else:
        print("✅ No Cursor-related paths found in PYTHONPATH")

    print_section("SUMMARY AND RECOMMENDATIONS")
    
    issues = []
    
    if os.environ.get("PYTHONHOME"):
        issues.append("PYTHONHOME is set, which can override standard Python paths")
    
    if os.environ.get("PYTHONPATH"):
        issues.append("PYTHONPATH is set, which may interfere with module imports")
        
    if not hasattr(sys, 'base_prefix') or sys.base_prefix == sys.prefix:
        issues.append("Not running in a virtual environment")
        
    if cursor_paths or (pythonpath and "cursor" in pythonpath.lower()):
        issues.append("Cursor-related paths may be affecting Python environment")
    
    if issues:
        print("❌ Found potential issues:")
        for issue in issues:
            print(f"  - {issue}")
        
        print("\nRecommendations:")
        print("  1. Run Python with clean environment variables:")
        print("     env -u PYTHONHOME -u PYTHONPATH python3")
        print("  2. Create a virtual environment:")
        print("     python3 -m venv venv && source venv/bin/activate")
        print("  3. Add clean environment aliases to your .bashrc:")
        print('     alias cleanpython="env -u PYTHONHOME -u PYTHONPATH python3"')
    else:
        print("✅ No significant issues detected")

if __name__ == "__main__":
    main() 