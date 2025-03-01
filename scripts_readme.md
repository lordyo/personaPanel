# Python Environment Scripts

This directory contains scripts to help manage Python environments and avoid common issues with Python configuration in Cursor.

## Issue Solved

These scripts address the following error that can occur when running Python in Cursor:
```
Fatal Python error: init_fs_encoding: failed to get the Python codec of the filesystem encoding
ModuleNotFoundError: No module named 'encodings'
```

This error is caused by conflicting Python environment variables (`PYTHONHOME` and `PYTHONPATH`) that can interfere with Python's ability to find its standard library.

## Scripts Available

### `run_python.sh`

Run Python scripts with a clean environment:

```bash
./run_python.sh backend/app.py
```

### `run_tests.sh`

Run Python tests with a clean environment:

```bash
# Run all tests
./run_tests.sh

# Run specific test file
./run_tests.sh tests/test_api_templates.py 

# Run tests with specific options
./run_tests.sh tests/ -v
```

### `venv.sh`

Activate the virtual environment with clean settings:

```bash
# Start a new shell with the virtual environment activated
./venv.sh

# Then you can run Python commands directly
python3 backend/app.py
pytest tests/
```

To exit the virtual environment, type `deactivate`.

## How These Scripts Work

These scripts:

1. Unset problematic environment variables (`PYTHONHOME` and `PYTHONPATH`)
2. Create a virtual environment if it doesn't exist
3. Install required dependencies from `requirements.txt`
4. Execute the Python command in the clean environment

This ensures Python can correctly find its standard libraries and modules. 