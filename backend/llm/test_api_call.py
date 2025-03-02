#!/usr/bin/env python3
import sys
import os
import json
import requests
from pprint import pprint

def test_api_entity_generation():
    """Test generating an entity through the backend API."""
    # Define the API endpoint for entity generation
    api_url = "http://localhost:5001/api/entities"
    
    # Prepare the example request data
    request_data = {
        "entity_type_id": "c91f4c75-55b3-4090-a987-cfb26193d468",  # Fantasy Character UUID
        "generate": True,
        "count": 1,
        "variability": 0.8,
        "entity_description": "A mysterious character from a fantasy novel with magical abilities."
    }
    
    print(f"Sending request to API: {api_url}")
    print(f"Request data: {json.dumps(request_data, indent=2)}")
    
    try:
        # Make the POST request to the API
        response = requests.post(api_url, json=request_data)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            result = response.json()
            print("API request successful!")
            
            # Check if the entity was generated successfully
            if result.get("status") == "success" and result.get("data"):
                generated_entity = result["data"][0]  # Get the first entity
                
                # Print the details of the generated entity
                print("\nGenerated Entity:")
                pprint(generated_entity)
                
                # Save the entity to an output file
                output_dir = os.path.join(os.path.dirname(__file__), "output")
                os.makedirs(output_dir, exist_ok=True)
                
                output_file = os.path.join(output_dir, "generated_entity.json")
                with open(output_file, "w") as f:
                    json.dump(generated_entity, f, indent=2)
                
                print(f"\nEntity saved to: {output_file}")
            else:
                print("Entity generation failed.")
                print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"API request failed with status code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def check_backend_health():
    """Check if the backend server is running."""
    try:
        response = requests.get("http://localhost:5001/api/health")
        if response.status_code == 200:
            return True
        return False
    except:
        return False

if __name__ == "__main__":
    # Check if the backend server is running
    if not check_backend_health():
        print("Backend server is not running. Please start the server before running this script.")
        sys.exit(1)
    
    # Run the entity generation test
    test_api_entity_generation() 