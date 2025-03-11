#!/usr/bin/env python3
"""
Test script to create a minimal batch simulation with a single entity.
This should complete quickly and verify our threading fixes.
"""

import requests
import sys
import json
import time

# API URL
API_URL = "http://localhost:5000/api"

def create_test_batch():
    """Create a minimal test batch simulation with a single entity."""
    # We'll use a specific entity type ID that we know has entities
    entity_type_id = "106f11c0-52a9-4ff5-9f95-b2b82de8fa11"
    
    try:
        # Get entities for this type
        response = requests.get(f"{API_URL}/entity-types/{entity_type_id}/entities")
        if response.status_code != 200:
            print(f"Error fetching entities: {response.text}")
            sys.exit(1)
        
        # Extract entity data from the response
        response_data = response.json()
        entity_data = response_data.get('data', [])
        
        print(f"Found {len(entity_data)} entities")
        
        if len(entity_data) < 1:
            print("No entities found, cannot proceed")
            sys.exit(1)
        
        # Just use one entity for a simple solo simulation
        entity_id = entity_data[0]['id']
        
        print(f"Using entity: {entity_id}")
        
        # Create a minimal batch simulation
        batch_data = {
            "name": f"SingleEntityTest_{int(time.time())}",
            "description": "Testing the batch simulation fix with a single entity",
            "context": "This is a minimal test with one entity, one turn, one round.",
            "entity_ids": [entity_id],
            "interaction_size": 1,  # Solo simulation
            "num_simulations": 1,
            "n_turns": 1,
            "simulation_rounds": 1
        }
        
        print(f"Creating batch simulation: {batch_data['name']}")
        response = requests.post(f"{API_URL}/batch-simulations", json=batch_data)
        
        if response.status_code != 201:
            print(f"Error creating batch: {response.text}")
            sys.exit(1)
            
        batch_result = response.json()
        batch_id = batch_result['data']['id']
        print(f"Batch created with ID: {batch_id}")
        
        # Poll for batch status every 2 seconds
        print("Waiting for batch to complete...")
        for _ in range(30):  # Try for up to 60 seconds
            response = requests.get(f"{API_URL}/batch-simulations/{batch_id}")
            if response.status_code != 200:
                print(f"Error fetching batch status: {response.text}")
                break
                
            batch_status = response.json()['data']['status']
            print(f"Current status: {batch_status}")
            
            if batch_status in ['completed', 'failed']:
                print(f"Batch finished with status: {batch_status}")
                if batch_status == 'completed':
                    print("SUCCESS: Batch processing is working correctly!")
                else:
                    print("ERROR: Batch processing failed. Check server logs.")
                break
                
            time.sleep(2)
        else:
            print("WARNING: Batch did not complete within the timeout period.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    create_test_batch() 