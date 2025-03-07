#!/bin/bash
# Run a sample simulation using the provided configuration and entities

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

# Directory for storing results
RESULTS_DIR="../../data/simulation_results"
mkdir -p "$RESULTS_DIR"

# Default configuration
CONFIG_FILE="sample_simulation_config.json"
ENTITIES_FILE="sample_entities.json"
DEFAULT_MODEL="gpt-4o-mini"

# Parse command-line options
while [[ $# -gt 0 ]]; do
    case "$1" in
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --entities)
            ENTITIES_FILE="$2"
            shift 2
            ;;
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

echo "Running simulation with:"
echo "  Config: $CONFIG_FILE"
echo "  Entities: $ENTITIES_FILE"
echo "  Model: $OPENAI_MODEL"
echo "  Output directory: $RESULTS_DIR"
echo

# Run the simulation
python3 run_simulation.py --config "$CONFIG_FILE" --entities "$ENTITIES_FILE" --output-dir "$RESULTS_DIR"

# Check if simulation was successful
if [ $? -eq 0 ]; then
    echo
    echo "✅ Simulation completed successfully!"
    echo "Results saved in $RESULTS_DIR"
else
    echo
    echo "❌ Simulation failed."
    exit 1
fi 