#!/bin/bash
# Test script for the dynamic entity generation implementation

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${YELLOW}===============================================${NC}"
    echo -e "${YELLOW}  $1${NC}"
    echo -e "${YELLOW}===============================================${NC}\n"
}

print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "\n${GREEN}✓ $2 completed successfully${NC}\n"
    else
        echo -e "\n${RED}✗ $2 failed with exit code $1${NC}\n"
    fi
}

# Kill any existing Flask server processes
echo -e "${BLUE}Checking for running Flask servers...${NC}"
pkill -f "flask run" || echo "No Flask servers running."

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}Error: Virtual environment not activated.${NC}"
    echo "Please make sure your virtual environment is set up correctly."
    echo "You can run: ./setup_python_env.sh to set it up."
    exit 1
fi

# Verify DSPy installation
echo -e "${BLUE}Verifying DSPy installation...${NC}"
if ! python3 -c "import dspy" &> /dev/null; then
    echo -e "${RED}Error: DSPy not installed in virtual environment.${NC}"
    echo "Installing DSPy now..."
    pip install dspy-ai
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install DSPy. Please install it manually:${NC}"
        echo "source venv/bin/activate && pip install dspy-ai"
        exit 1
    fi
    echo -e "${GREEN}DSPy installed successfully.${NC}"
else
    DSPY_VERSION=$(python3 -c "import dspy; print(dspy.__version__)")
    echo -e "${GREEN}DSPy version ${DSPY_VERSION} is installed.${NC}"
fi

# Check for API key in .env
if ! grep -q "OPENAI_API_KEY" .env; then
    echo -e "${RED}Warning: OPENAI_API_KEY not found in .env file.${NC}"
    echo "Make sure your API key is properly set up before running tests."
    exit 1
fi

# Run the dynamic signature test
print_header "Testing Dynamic Signature Entity Generation"
python3 backend/llm/test_dynamic_signature.py
DYNAMIC_SIG_RESULT=$?
print_status $DYNAMIC_SIG_RESULT "Dynamic Signature Entity Generation Test"

# Final summary
echo -e "\n${YELLOW}===============================================${NC}"
echo -e "${YELLOW}  Test Summary${NC}"
echo -e "${YELLOW}===============================================${NC}"
if [ $DYNAMIC_SIG_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Dynamic Signature Entity Generation Test: PASSED${NC}"
else
    echo -e "${RED}✗ Dynamic Signature Entity Generation Test: FAILED${NC}"
fi

# Deactivate virtual environment
deactivate
echo -e "${GREEN}Tests completed.${NC}" 