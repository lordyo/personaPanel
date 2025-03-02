#!/bin/bash
# This script runs the DSPy test scripts using the project's virtual environment

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
    pip install dspy
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install DSPy. Please install it manually:${NC}"
        echo "source venv/bin/activate && pip install dspy"
        exit 1
    fi
    echo -e "${GREEN}DSPy installed successfully.${NC}"
else
    DSPY_VERSION=$(python3 -c "import dspy; print(dspy.__version__)")
    echo -e "${GREEN}DSPy version ${DSPY_VERSION} is installed.${NC}"
fi

# Kill any existing Flask server processes
echo -e "${BLUE}Checking for running Flask servers...${NC}"
pkill -f "flask run" || echo "No Flask servers running."

# Check for API key in .env
if ! grep -q "OPENAI_API_KEY" .env; then
    echo -e "${RED}Warning: OPENAI_API_KEY not found in .env file.${NC}"
    echo "Make sure your API key is properly set up before running tests."
fi

# Display choices
print_header "Available DSPy Tests"
echo -e "${CYAN}1)${NC} Simple DSPy Test - Basic functionality test"
echo -e "${CYAN}2)${NC} Simple Entity Creator - Basic entity creation with name and backstory"
echo -e "${CYAN}3)${NC} All Tests - Run all tests sequentially"
echo -e "${CYAN}q)${NC} Quit"

# Ask which test to run
read -p "Enter your choice (1, 2, 3, or q): " choice

# Run the selected test
case "$choice" in
    1)
        print_header "Running Simple DSPy Test"
        python3 backend/llm/simple_dspy_test.py
        print_status $? "Simple DSPy Test"
        ;;
    2)
        print_header "Running Simple Entity Creator Test"
        python3 backend/llm/simple_entity_creator.py
        print_status $? "Simple Entity Creator Test"
        ;;
    3)
        print_header "Running All Tests"
        
        print_header "Simple DSPy Test"
        python3 backend/llm/simple_dspy_test.py
        SIMPLE_TEST_RESULT=$?
        print_status $SIMPLE_TEST_RESULT "Simple DSPy Test"
        
        print_header "Simple Entity Creator Test"
        python3 backend/llm/simple_entity_creator.py
        SIMPLE_ENTITY_RESULT=$?
        print_status $SIMPLE_ENTITY_RESULT "Simple Entity Creator Test"
        
        # Final summary
        echo -e "\n${YELLOW}===============================================${NC}"
        echo -e "${YELLOW}  Test Summary${NC}"
        echo -e "${YELLOW}===============================================${NC}"
        if [ $SIMPLE_TEST_RESULT -eq 0 ]; then
            echo -e "${GREEN}✓ Simple DSPy Test: PASSED${NC}"
        else
            echo -e "${RED}✗ Simple DSPy Test: FAILED${NC}"
        fi
        
        if [ $SIMPLE_ENTITY_RESULT -eq 0 ]; then
            echo -e "${GREEN}✓ Simple Entity Creator Test: PASSED${NC}"
        else
            echo -e "${RED}✗ Simple Entity Creator Test: FAILED${NC}"
        fi
        ;;
    q|Q)
        echo "Exiting."
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

# Deactivate virtual environment
deactivate
echo -e "${GREEN}Tests completed.${NC}" 