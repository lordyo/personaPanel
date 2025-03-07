#!/bin/bash
# Run the simulation tests

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
        --entities)
            ENTITIES_FILE="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--model MODEL] [--entities FILE] [--output-dir DIR]"
            exit 1
            ;;
    esac
done

# Set default model if not specified
if [ -z "$OPENAI_MODEL" ]; then
    export OPENAI_MODEL="$DEFAULT_MODEL"
fi

# Set default entities file if not specified
if [ -z "$ENTITIES_FILE" ]; then
    ENTITIES_FILE="../../config/example_entities.json"
fi

# Set default output directory if not specified
if [ -z "$OUTPUT_DIR" ]; then
    OUTPUT_DIR="../../data/test_results"
fi

echo "Running simulation tests with:"
echo "  Model: $OPENAI_MODEL"
echo "  Entities: $ENTITIES_FILE"
echo "  Output directory: $OUTPUT_DIR"
echo

# Make sure output directory exists
mkdir -p "$OUTPUT_DIR"

# Check if test script exists
if [ ! -f "run_simulation_tests.py" ]; then
    echo "Error: run_simulation_tests.py not found in the current directory."
    exit 1
fi

# Kill existing servers
echo "Checking for existing Python processes..."
pkill -f "python3.*simulation" || true
echo "Continuing with tests..."

# Run the tests
python3 run_simulation_tests.py --entities "$ENTITIES_FILE" --output-dir "$OUTPUT_DIR"

# Check if tests were successful
if [ $? -eq 0 ]; then
    echo
    echo "✅ All simulation tests completed successfully!"
else
    echo
    echo "❌ Some simulation tests failed. Check the logs for details."
    exit 1
fi 