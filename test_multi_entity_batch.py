#!/usr/bin/env python3
"""
Test script to create a batch simulation with multiple entities.
"""

import requests
import sys
import json
import time

# API URL
API_URL = "http://localhost:5000/api"

def create_multi_entity_batch():
    """Create a test batch simulation with multiple entities."""
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
        
        if len(entity_data) < 3:
            print("Not enough entities found (need at least 3)")
            sys.exit(1)
        
        # Use three entities for a group simulation
        entity_ids = [entity['id'] for entity in entity_data[:3]]
        
        print(f"Using {len(entity_ids)} entities")
        
        # Create a batch simulation
        batch_data = {
            "name": f"MultiEntityTest_{int(time.time())}",
            "description": "Testing the batch simulation fix with multiple entities",
            "context": "This is a test discussion about improving HR practices in the company.",
            "entity_ids": entity_ids,
            "interaction_size": 3,  # Group simulation with 3 entities
            "num_simulations": 1,
            "n_turns": 2,  # Multiple turns
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
        
        # Poll for batch status every 3 seconds
        print("Waiting for batch to complete...")
        for i in range(20):  # Try for up to 60 seconds
            response = requests.get(f"{API_URL}/batch-simulations/{batch_id}")
            if response.status_code != 200:
                print(f"Error fetching batch status: {response.text}")
                break
                
            batch_status = response.json()['data']['status']
            print(f"Current status ({i+1}/20 checks): {batch_status}")
            
            if batch_status in ['completed', 'failed']:
                print(f"Batch finished with status: {batch_status}")
                if batch_status == 'completed':
                    print("SUCCESS: Batch processing is working correctly!")
                    # Check if simulations were created
                    simulations = response.json()['data'].get('simulations', [])
                    print(f"Number of simulations: {len(simulations)}")
                else:
                    print("ERROR: Batch processing failed. Check server logs.")
                break
                
            time.sleep(3)
        else:
            print("WARNING: Batch did not complete within the timeout period.")
        
        print(f"\nYou can check the batch details with: python3 inspect_batch.py {batch_id}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    create_multi_entity_batch() 