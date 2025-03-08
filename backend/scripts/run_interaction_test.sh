#!/bin/bash
# Script to run the interaction module test

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Navigate to project root
cd "$(dirname "$0")/../.."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found.${NC}"
    echo "Please run: ./setup_python_env.sh to set up the environment."
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}Error: Virtual environment not activated.${NC}"
    echo "Please make sure your virtual environment is set up correctly."
    exit 1
fi

# Check for required packages
echo -e "${BLUE}Checking required packages...${NC}"
python3 -c "import dspy" &> /dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}DSPy not found, installing...${NC}"
    pip install dspy-ai python-dotenv
fi

# Check for API key in .env
if ! grep -q "OPENAI_API_KEY" .env &> /dev/null; then
    echo -e "${YELLOW}Warning: OPENAI_API_KEY not found in .env file.${NC}"
    echo "Make sure your API key is properly set up before running tests."
fi

# Run the test
echo -e "${BLUE}Running interaction module test...${NC}"
python3 backend/scripts/test_interaction_module.py

# Capture exit code
exit_code=$?

# Print result
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}Test completed successfully!${NC}"
else
    echo -e "${RED}Test failed with exit code: $exit_code${NC}"
fi

# Deactivate virtual environment
deactivate

exit $exit_code 