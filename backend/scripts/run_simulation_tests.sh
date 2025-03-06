#!/bin/bash
# Run the basic simulation tests

# Ensure we're in a Python virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Python virtual environment not active. Please activate your virtual environment first."
    echo "You can use: source venv/bin/activate"
    exit 1
fi

# Navigate to the scripts directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR" || exit

# Load environment variables from .env file in root directory
ENV_FILE="../../.env"
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment variables from $ENV_FILE"
    # Use a temporary file to avoid export issues
    grep -v '^#' "$ENV_FILE" | grep -v '^\s*$' > .env_temp
    while IFS='=' read -r key value; do
        # Remove any comments after the value
        value=$(echo "$value" | sed 's/\s*#.*$//')
        # Remove surrounding quotes if present
        value=$(echo "$value" | sed 's/^"\(.*\)"$/\1/' | sed "s/^'\(.*\)'$/\1/")
        export "$key=$value"
    done < .env_temp
    rm .env_temp
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "OPENAI_API_KEY environment variable not set."
    echo "Please set it with: export OPENAI_API_KEY='your-api-key' or add it to the .env file in the root directory."
    exit 1
fi

# Default model
DEFAULT_MODEL="gpt-4o-mini"

# Parse command-line options
while [[ $# -gt 0 ]]; do
    case "$1" in
        --model)
            export OPENAI_MODEL="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Set default model if not specified
if [ -z "$OPENAI_MODEL" ]; then
    export OPENAI_MODEL="$DEFAULT_MODEL"
fi

echo "Running basic simulation tests with model: $OPENAI_MODEL"
echo

# Run the tests
python3 test_simulation.py

# Check if tests were successful
if [ $? -eq 0 ]; then
    echo
    echo "✅ Basic simulations completed successfully!"
    echo "Results saved in simulation_results directory"
else
    echo
    echo "❌ Basic simulations failed."
    exit 1
fi 