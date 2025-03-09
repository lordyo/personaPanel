#!/bin/bash
# Advanced batch simulation script with support for turns and rounds

# Set up venv
source venv/bin/activate

# Set default values
DEFAULT_ENTITIES_FILE="entity_ids.json"
DEFAULT_CONTEXT="A group discussion about climate change solutions"
DEFAULT_INTERACTION_SIZE=2
DEFAULT_NUM_SIMULATIONS=3
DEFAULT_NAME="Advanced Batch Simulation"
DEFAULT_DESCRIPTION="A batch simulation with multiple turns and rounds"
DEFAULT_N_TURNS=2
DEFAULT_SIMULATION_ROUNDS=2

# Parse command line arguments
ENTITIES=${1:-$DEFAULT_ENTITIES_FILE}
CONTEXT=${2:-$DEFAULT_CONTEXT}
INTERACTION_SIZE=${3:-$DEFAULT_INTERACTION_SIZE}
NUM_SIMULATIONS=${4:-$DEFAULT_NUM_SIMULATIONS}
NAME=${5:-$DEFAULT_NAME}
DESCRIPTION=${6:-$DEFAULT_DESCRIPTION}
N_TURNS=${7:-$DEFAULT_N_TURNS}
SIMULATION_ROUNDS=${8:-$DEFAULT_SIMULATION_ROUNDS}

# Initialize the database to ensure all required tables exist
echo "Initializing database to ensure all tables exist..."
python3 initialize_db.py

# Create entity IDs file if it doesn't exist
if [ ! -f "$ENTITIES" ] && [[ "$ENTITIES" == *.json ]]; then
    echo "Creating sample entity IDs file..."
    # Create some dummy entity IDs for testing
    python3 -c "
import json
import uuid

# Create some dummy entity IDs for testing
entity_ids = [str(uuid.uuid4()) for _ in range(5)]

# Save the entity IDs to file
with open('$ENTITIES', 'w') as f:
    json.dump(entity_ids, f)
    
print(f'Created {len(entity_ids)} dummy entity IDs in {\"$ENTITIES\"}')
"
fi

# Run the batch simulation
echo "Running advanced batch simulation with:"
echo "  Entities: $ENTITIES"
echo "  Context: $CONTEXT"
echo "  Interaction size: $INTERACTION_SIZE"
echo "  Number of simulations: $NUM_SIMULATIONS"
echo "  Name: $NAME"
echo "  Description: $DESCRIPTION"
echo "  Number of turns: $N_TURNS"
echo "  Simulation rounds: $SIMULATION_ROUNDS"
echo

python3 backend/scripts/run_batch_simulation.py \
    --entities "$ENTITIES" \
    --context "$CONTEXT" \
    --interaction-size "$INTERACTION_SIZE" \
    --num-simulations "$NUM_SIMULATIONS" \
    --name "$NAME" \
    --description "$DESCRIPTION" \
    --n-turns "$N_TURNS" \
    --simulation-rounds "$SIMULATION_ROUNDS"

# Check for success
if [ $? -eq 0 ]; then
    echo
    echo "✅ Advanced batch simulation completed successfully!"
    echo "Check the database or API for results."
else
    echo
    echo "❌ Advanced batch simulation failed."
    exit 1
fi 