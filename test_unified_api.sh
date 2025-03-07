#!/bin/bash

# Test script for the unified simulation API
echo "Testing Unified Simulation API..."

# Set the API base URL
BASE_URL="http://localhost:5001/api"

# Colors for better output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to make an API call and display results
call_api() {
    local method=$1
    local endpoint=$2
    local data=$3
    local label=$4
    
    echo -e "\n${YELLOW}Testing $label${NC}"
    echo "Endpoint: $method $endpoint"
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -X GET "$BASE_URL$endpoint")
    else
        echo "Data: $data"
        response=$(curl -s -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    if [[ $response == *"error"* ]]; then
        echo -e "${RED}ERROR: $response${NC}"
        return 1
    else
        echo -e "${GREEN}SUCCESS${NC}"
        echo "Response: $response"
        # Extract ID using jq if the response is valid JSON
        if [[ $response == *"data"*"id"* ]] && command -v jq &> /dev/null; then
            id=$(echo $response | jq -r '.data.id // empty')
            if [[ ! -z "$id" ]]; then
                echo "Extracted ID: $id"
                echo $id > .test_id
            fi
        fi
        return 0
    fi
}

# Check and fetch existing entities
check_and_fetch_entities() {
    echo -e "\n${YELLOW}Fetching existing entities...${NC}"
    
    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}Error: jq is not installed. Please install it with: sudo apt install jq${NC}"
        return 1
    fi
    
    # Get list of entity types
    response=$(curl -s -X GET "$BASE_URL/entity-types")
    
    if [[ $response == *"error"* ]]; then
        echo -e "${RED}Error fetching entity types: $response${NC}"
        return 1
    fi
    
    # Get the total number of entity types
    entity_type_count=$(echo $response | jq '.data | length')
    
    # Try each entity type until we find one with enough entities
    for ((i=0; i<$entity_type_count; i++)); do
        entity_type_id=$(echo $response | jq -r ".data[$i].id")
        entity_type_name=$(echo $response | jq -r ".data[$i].name")
        
        echo "Trying entity type: $entity_type_name ($entity_type_id)"
        
        # Get entities of this type
        entities_response=$(curl -s -X GET "$BASE_URL/entity-types/$entity_type_id/entities")
        
        # Extract entities using jq
        entity_count=$(echo $entities_response | jq '.data | length')
        
        echo "Found $entity_count entities"
        
        if [[ $entity_count -ge 3 ]]; then
            echo -e "${GREEN}Found entity type with at least 3 entities: $entity_type_name${NC}"
            
            # Extract and save the first 3 entity IDs
            echo $entities_response | jq -r '.data[0:3][].id' > .test_entities
            return 0
        fi
    done
    
    echo -e "${RED}No entity type found with at least 3 entities${NC}"
    return 1
}

# Test 1: Create a unified simulation
test_create_unified_simulation() {
    # Get entity IDs
    readarray -t entity_array < .test_entities
    
    # Make sure we have at least 3 entities
    if [[ ${#entity_array[@]} -lt 3 ]]; then
        echo -e "${RED}Not enough entities found for testing. Need at least 3.${NC}"
        return 1
    fi
    
    local data="{
        \"context\": \"A conference panel on artificial intelligence ethics\",
        \"entities\": [\"${entity_array[0]}\", \"${entity_array[1]}\", \"${entity_array[2]}\"],
        \"n_turns\": 2,
        \"simulation_rounds\": 1,
        \"metadata\": {
            \"category\": \"tech\",
            \"audience\": \"academic\"
        }
    }"
    
    call_api "POST" "/unified-simulations" "$data" "Create Unified Simulation"
}

# Test 2: Get the created simulation
test_get_unified_simulation() {
    local id=$(cat .test_id)
    call_api "GET" "/unified-simulations/$id" "" "Get Unified Simulation"
}

# Test 3: Continue the simulation
test_continue_simulation() {
    local id=$(cat .test_id)
    local data='{
        "n_turns": 1,
        "simulation_rounds": 1
    }'
    
    call_api "POST" "/unified-simulations/$id/continue" "$data" "Continue Unified Simulation"
}

# Test 4: List all simulations
test_list_unified_simulations() {
    call_api "GET" "/unified-simulations" "" "List All Unified Simulations"
}

# Test 5: List simulations with filters
test_list_filtered_simulations() {
    call_api "GET" "/unified-simulations?interaction_type=group&limit=5" "" "List Filtered Simulations"
}

# Main test sequence
echo "Starting tests..."
check_and_fetch_entities || exit 1
test_create_unified_simulation || exit 1
test_get_unified_simulation || exit 1
test_continue_simulation || exit 1
test_list_unified_simulations || exit 1
test_list_filtered_simulations || exit 1

# Clean up
rm -f .test_id .test_entities

echo -e "\n${GREEN}All tests completed!${NC}" 