#!/usr/bin/env python3
"""
Test script for batch simulation API with interaction_type and language parameters.
"""

import requests
import json
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API endpoint
API_URL = "http://localhost:5000/api/batch-simulations"

def test_batch_simulation_creation():
    """Test creating a batch simulation with interaction_type and language parameters."""
    
    # Get entity IDs to use in the simulation
    # For this test, we'll use the first API endpoint to get entity types,
    # then get entities of the first type
    try:
        # Get entity types
        entity_types_response = requests.get("http://localhost:5000/api/entity-types")
        entity_types = entity_types_response.json()["data"]
        
        if not entity_types:
            logger.error("No entity types found")
            return False
        
        # Get first entity type ID
        entity_type_id = entity_types[0]["id"]
        logger.info(f"Using entity type: {entity_types[0]['name']}")
        
        # Get entities of this type
        entities_response = requests.get(f"http://localhost:5000/api/entities?entity_type_id={entity_type_id}")
        entities = entities_response.json()["data"]
        
        if not entities or len(entities) < 2:
            logger.error(f"Not enough entities found for entity type {entity_type_id}")
            return False
        
        # Use first two entities
        entity_ids = [entities[0]["id"], entities[1]["id"]]
        logger.info(f"Using entities: {entities[0]['name']} and {entities[1]['name']}")
        
        # Create batch simulation request data
        batch_data = {
            "name": "Test Batch with Interaction Type and Language",
            "description": "Testing batch simulation with new parameters",
            "context": "Test conversation to verify interaction_type and language parameters",
            "entity_ids": entity_ids,
            "interaction_size": 2,
            "num_simulations": 1,
            "n_turns": 1,
            "simulation_rounds": 1,
            "interaction_type": "debate",
            "language": "Spanish",
            "metadata": {
                "test": True
            }
        }
        
        # Log the request data
        logger.info(f"Sending POST request with data: {json.dumps(batch_data, indent=2)}")
        
        # Create batch simulation
        response = requests.post(API_URL, json=batch_data)
        
        # Log the response status and data
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response data: {response.text}")
        
        if response.status_code != 201:
            logger.error(f"Failed to create batch simulation: {response.text}")
            return False
        
        batch_id = response.json()["data"]["id"]
        logger.info(f"Successfully created batch simulation with ID: {batch_id}")
        
        # Optional: Wait and check the batch status
        import time
        time.sleep(2)  # Give it a moment to start processing
        
        status_response = requests.get(f"{API_URL}/{batch_id}")
        logger.info(f"Batch status: {status_response.json()['data']['status']}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing batch simulation: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("Starting batch simulation API test")
    
    success = test_batch_simulation_creation()
    
    if success:
        logger.info("Test completed successfully")
        sys.exit(0)
    else:
        logger.error("Test failed")
        sys.exit(1) 