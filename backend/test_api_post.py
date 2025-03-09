#!/usr/bin/env python3
"""
Test script for posting to the batch entity generation API endpoint.
"""

import requests
import json
import sys

def test_batch_generation():
    """Test the batch entity generation endpoint with a POST request."""
    # URL of the API endpoint
    url = "http://localhost:5000/api/batch-entities/generate"
    
    # Test data
    data = {
        "entity_type": "character",
        "entity_description": "A fictional character for a fantasy RPG game",
        "dimensions": [
            {
                "name": "age",
                "type": "numeric",
                "min": 18,
                "max": 80,
                "description": "Age of the character in years"
            },
            {
                "name": "class",
                "type": "categorical",
                "options": ["Warrior", "Mage", "Rogue", "Cleric", "Ranger"],
                "description": "The character's class or profession in the game world"
            },
            {
                "name": "alignment",
                "type": "categorical",
                "options": ["Lawful Good", "Neutral Good", "Chaotic Good", "Lawful Neutral", "True Neutral", "Chaotic Neutral", "Lawful Evil", "Neutral Evil", "Chaotic Evil"],
                "description": "The character's moral and ethical alignment"
            }
        ],
        "output_fields": [
            {
                "name": "appearance",
                "description": "Physical description of the character"
            },
            {
                "name": "abilities",
                "description": "Special abilities or skills this character possesses"
            }
        ],
        "batch_size": 2,
        "variability": 0.7
    }
    
    # Print request info
    print(f"Sending POST request to {url}")
    
    try:
        # Send the POST request
        response = requests.post(url, json=data)
        
        # Print the status code
        print(f"Response status code: {response.status_code}")
        
        # Print the response
        if response.status_code == 200:
            response_data = response.json()
            
            # Pretty print the response with indentation
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            # Check if we have entities
            if "entities" in response_data and len(response_data["entities"]) > 0:
                print(f"\nGenerated {len(response_data['entities'])} entities:")
                for i, entity in enumerate(response_data["entities"]):
                    print(f"\n--- Entity {i+1}: {entity['name']} ---")
                    print(f"Backstory: {entity['backstory']}")
                    
                    # Print additional fields
                    for field_name in ["appearance", "abilities"]:
                        if field_name in entity:
                            print(f"{field_name.capitalize()}: {entity[field_name]}")
                    
                    # Print dimensions
                    if "dimensions" in entity:
                        print("\nDimension values:")
                        for dim_name, dim_value in entity["dimensions"].items():
                            print(f"  - {dim_name}: {dim_value}")
            else:
                print("No entities found in the response")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_batch_generation() 