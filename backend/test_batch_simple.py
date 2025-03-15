#!/usr/bin/env python3
"""
Simple test script for batch simulation API with interaction_type and language parameters.
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
    
    try:
        # Use hardcoded entity IDs for testing
        # These should be replaced with actual entity IDs from your database
        entity_ids = ["entity1", "entity2"]
        
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