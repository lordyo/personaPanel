#!/bin/bash

# Simple test script for the unified simulation API
echo "Testing Unified Simulation API..."

# Set the API base URL
BASE_URL="http://localhost:5001/api"

# Hard-coded entity IDs from a known Human entity type
ENTITY_1="406f8245-aec8-4da5-bd34-e13cc97040e8"
ENTITY_2="6a3b61f8-2c89-4a17-b0c6-305bf060ef52"
ENTITY_3="b128964e-d00a-4393-8670-4a2988340166"

# Colors for better output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test: Create a unified simulation
echo -e "\n${YELLOW}Testing Create Unified Simulation${NC}"
echo "Endpoint: POST /unified-simulations"

DATA="{
    \"context\": \"A conference panel on artificial intelligence ethics\",
    \"entities\": [\"$ENTITY_1\", \"$ENTITY_2\", \"$ENTITY_3\"],
    \"n_turns\": 2,
    \"simulation_rounds\": 1,
    \"metadata\": {
        \"category\": \"tech\",
        \"audience\": \"academic\"
    }
}"

echo "Data: $DATA"

RESPONSE=$(curl -s -X POST "$BASE_URL/unified-simulations" \
    -H "Content-Type: application/json" \
    -d "$DATA")

if [[ $RESPONSE == *"error"* ]]; then
    echo -e "${RED}ERROR: $RESPONSE${NC}"
    exit 1
else
    echo -e "${GREEN}SUCCESS${NC}"
    echo "Response: $RESPONSE"
fi

echo -e "\n${GREEN}Test completed!${NC}" 