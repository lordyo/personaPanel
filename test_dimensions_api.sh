#!/bin/bash
# Test script for entity type dimensions API

# Set terminal colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Entity Type Dimensions API Test ===${NC}"

# Check if the API is running
if ! curl -s http://localhost:5001/api/health > /dev/null; then
  echo -e "${RED}Error: API server is not running on port 5001${NC}"
  echo "Please start the server with: ./run-app"
  exit 1
fi

echo -e "${GREEN}API server is running. Proceeding with tests...${NC}"

# Test 1: Generate dimensions for a Fantasy Character
echo -e "\n${BLUE}Test 1: Generate dimensions for a Fantasy Character${NC}"
./backend/scripts/test_api_dimensions.py \
  --name "Fantasy Character" \
  --description "A detailed fantasy character that could be used in a role-playing game or fantasy novel. This includes characteristics like class, race, abilities, personality traits, and background." \
  --dimensions 8 \
  --output "test_fantasy_character_dimensions.json"

# Test 2: Generate dimensions for a Sci-Fi Robot
echo -e "\n${BLUE}Test 2: Generate dimensions for a Sci-Fi Robot${NC}"
./backend/scripts/test_api_dimensions.py \
  --name "Sci-Fi Robot" \
  --description "A futuristic robot with artificial intelligence, designed for various tasks in a science fiction setting." \
  --dimensions 6 \
  --output "test_scifi_robot_dimensions.json"

# Test 3: Generate dimensions for a Magical Creature
echo -e "\n${BLUE}Test 3: Generate dimensions for a Magical Creature${NC}"
./backend/scripts/test_api_dimensions.py \
  --name "Magical Creature" \
  --description "A mythical beast with magical properties, existing in a fantasy world with its own unique characteristics and abilities." \
  --dimensions 7 \
  --output "test_magical_creature_dimensions.json"

# Test 4: Generate AND create an entity type directly
echo -e "\n${BLUE}Test 4: Generate and create a Modern Superhero entity type${NC}"
curl -X POST http://localhost:5001/api/entity-types/generate-and-create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Modern Superhero", 
    "description": "A contemporary superhero character with unique powers, backstory, and characteristics, suitable for modern storytelling in comics, TV shows, or movies.", 
    "n_dimensions": 8
  }' | jq . > test_superhero_entity_type.json

echo -e "\n${GREEN}All tests completed. Check the output files for results.${NC}"
echo "- test_fantasy_character_dimensions.json"
echo "- test_scifi_robot_dimensions.json"
echo "- test_magical_creature_dimensions.json"
echo "- test_superhero_entity_type.json (generated AND created in the database)" 