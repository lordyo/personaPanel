#!/usr/bin/env python3
"""
Test script to verify the batch simulation fix.
This script will make a request to the batch simulation API endpoint.
"""

import requests
import sys
import json
import time

# API URL
API_URL = "http://localhost:5000/api"

def test_batch_create():
    """Test creating a batch simulation and verify no duplicates are created."""
    # We'll use a specific entity type ID that we know has entities
    entity_type_id = "106f11c0-52a9-4ff5-9f95-b2b82de8fa11"
    
    try:
        # Get the entity type details
        response = requests.get(f"{API_URL}/entity-types/{entity_type_id}")
        if response.status_code != 200:
            print(f"Error fetching entity type: {response.text}")
            sys.exit(1)
        
        entity_type = response.json().get('data', {})
        print(f"Using entity type: {entity_type.get('name', 'Unknown')} ({entity_type_id})")
        
        # Get entities for this type
        response = requests.get(f"{API_URL}/entity-types/{entity_type_id}/entities")
        if response.status_code != 200:
            print(f"Error fetching entities: {response.text}")
            sys.exit(1)
        
        # Extract entity data from the response
        response_data = response.json()
        entity_data = response_data.get('data', [])
        
        print(f"Found {len(entity_data)} entities")
        
        if len(entity_data) < 2:
            print("Not enough entities found (need at least 2)")
            sys.exit(1)
        
        # Take at most 5 entities
        entity_ids = []
        for i, entity in enumerate(entity_data):
            if i >= 5:  # Limit to 5 entities
                break
            entity_ids.append(entity['id'])
        
        print(f"Using {len(entity_ids)} entities: {entity_ids}")
        
        # Create a batch simulation
        batch_data = {
            "name": f"Test Batch Fix {int(time.time())}",
            "description": "Testing the batch simulation fix",
            "context": "This is a test batch simulation to verify the fix for duplicate batches.",
            "entity_ids": entity_ids,
            "interaction_size": 2,
            "num_simulations": 2,
            "n_turns": 1,
            "simulation_rounds": 1,
            "metadata": {
                "test": True,
                "fix_version": "1.0"
            }
        }
        
        print(f"Creating batch simulation: {batch_data['name']}")
        response = requests.post(f"{API_URL}/batch-simulations", json=batch_data)
        
        if response.status_code != 201:
            print(f"Error creating batch: {response.text}")
            sys.exit(1)
            
        batch_result = response.json()
        print(f"Batch created: {json.dumps(batch_result, indent=2)}")
        
        batch_id = batch_result['data']['id']
        
        # Wait a moment for processing to start
        print("Waiting for batch to start processing...")
        time.sleep(2)
        
        # Get all batches and check for duplicates
        response = requests.get(f"{API_URL}/batch-simulations")
        if response.status_code != 200:
            print(f"Error fetching batches: {response.text}")
            sys.exit(1)
            
        batches = response.json()['data']
        
        # Check for batches with the same name
        batch_name = batch_data['name']
        matching_batches = [b for b in batches if b['name'] == batch_name]
        
        if len(matching_batches) > 1:
            print(f"ERROR: Found {len(matching_batches)} batches with name '{batch_name}'")
            for batch in matching_batches:
                print(f"  ID: {batch['id']}, Status: {batch['status']}, Created: {batch['created_at']}")
            print("The fix didn't work! We still have duplicate batches.")
        else:
            print(f"SUCCESS: Found exactly 1 batch with name '{batch_name}'")
            print(f"  ID: {matching_batches[0]['id']}, Status: {matching_batches[0]['status']}")
            print("The fix worked! No duplicate batches were created.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_batch_create() 