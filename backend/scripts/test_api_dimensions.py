#!/usr/bin/env python3
"""
Test script for the entity type dimensions suggestion API endpoint.

This script tests the API endpoint for generating entity type dimensions.
"""

import sys
import json
import argparse
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Test the entity type dimensions suggestion API endpoint')
    
    parser.add_argument('--url', '-u', 
                        type=str, 
                        default='http://localhost:5001/api/entity-types/suggest-dimensions',
                        help='URL of the API endpoint')
    
    parser.add_argument('--input', '-i', 
                        type=str, 
                        help='Path to input JSON file with entity type information')
    
    parser.add_argument('--output', '-o',
                        type=str, 
                        default='api_dimensions_output.json',
                        help='Path to save the API response (default: api_dimensions_output.json)')
    
    parser.add_argument('--name', '-n',
                        type=str,
                        help='Entity type name (overrides file input if provided)')
    
    parser.add_argument('--description', '-d',
                        type=str,
                        help='Entity type description (overrides file input if provided)')
    
    parser.add_argument('--dimensions', '-dim',
                        type=int,
                        default=5,
                        help='Number of dimensions to generate (default: 5)')
    
    return parser.parse_args()


def main():
    """Main function to run the API test."""
    args = parse_args()
    
    # Initialize parameters
    entity_type_name = None
    entity_type_description = None
    n_dimensions = args.dimensions
    
    # Get entity type information from file if provided
    if args.input:
        try:
            with open(args.input, 'r') as f:
                input_data = json.load(f)
                entity_type_name = input_data.get('entity_type_name')
                entity_type_description = input_data.get('entity_type_description')
                n_dimensions = input_data.get('n_dimensions', n_dimensions)
        except Exception as e:
            logger.error(f"Error reading input file: {e}")
            return
    
    # Override with command line arguments if provided
    if args.name:
        entity_type_name = args.name
    if args.description:
        entity_type_description = args.description
    
    # Validate we have the required parameters
    if not entity_type_name:
        logger.error("Entity type name is required")
        return
    
    # Prepare the request payload
    payload = {
        "name": entity_type_name,
        "description": entity_type_description or "",
        "n_dimensions": n_dimensions
    }
    
    logger.info(f"Sending request to {args.url}")
    logger.info(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Send the request to the API
        response = requests.post(args.url, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response
            response_data = response.json()
            
            # Print the response
            logger.info(f"API Response Status Code: {response.status_code}")
            if 'data' in response_data:
                data = response_data['data']
                
                # Print the generated dimensions
                if 'dimensions' in data:
                    dimensions = data['dimensions']
                    logger.info(f"Generated {len(dimensions)} dimensions:")
                    for i, dim in enumerate(dimensions, 1):
                        logger.info(f"Dimension {i}: {dim.get('name')} ({dim.get('type')})")
                
                # Save the response to the output file
                with open(args.output, 'w') as f:
                    json.dump(response_data, f, indent=2)
                
                logger.info(f"Saved API response to {args.output}")
            else:
                logger.error(f"Unexpected response format: {response_data}")
        else:
            # If the request failed, print the error
            logger.error(f"API request failed with status code {response.status_code}")
            logger.error(f"Response: {response.text}")
    
    except Exception as e:
        logger.error(f"Error making API request: {e}")


if __name__ == "__main__":
    main() 