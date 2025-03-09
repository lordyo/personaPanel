#!/usr/bin/env python3
"""
Test script for the batch entity generation API endpoint.
"""

import requests
import json
import sys

def test_batch_endpoint():
    """Test the batch entity generation API endpoint."""
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
    
    # Send POST request
    print(f"Sending POST request to {url}")
    print(f"Request data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data)
        
        # Print the response status and content
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        else:
            print(f"Response text: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_batch_endpoint() 