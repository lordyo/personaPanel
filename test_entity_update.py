#!/usr/bin/env python3
"""
Test script for entity update functionality.
"""

import requests
import json
import sys
import datetime

# Configuration
BASE_URL = "http://localhost:5001/api"

def test_update_entity(entity_id):
    """Test updating an entity with the given ID."""
    
    # First, get the current entity data
    response = requests.get(f"{BASE_URL}/entities/{entity_id}")
    if response.status_code != 200:
        print(f"Error getting entity: {response.status_code}")
        print(response.text)
        return False
    
    entity = response.json()["data"]
    print(f"Original entity: {json.dumps(entity, indent=2)}")
    
    # Prepare updated data - add a test attribute
    if "attributes" in entity:
        entity["attributes"]["test_update"] = f"Updated at {datetime.datetime.now()}"
    else:
        entity["attributes"] = {"test_update": f"Updated at {datetime.datetime.now()}"}
    
    # Update the entity
    response = requests.put(f"{BASE_URL}/entities/{entity_id}", json=entity)
    if response.status_code != 200:
        print(f"Error updating entity: {response.status_code}")
        print(response.text)
        return False
    
    updated_entity = response.json()["data"]
    print(f"Updated entity: {json.dumps(updated_entity, indent=2)}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_entity_update.py <entity_id>")
        sys.exit(1)
    
    entity_id = sys.argv[1]
    success = test_update_entity(entity_id)
    if success:
        print("Entity update test successful!")
    else:
        print("Entity update test failed!")
        sys.exit(1) 