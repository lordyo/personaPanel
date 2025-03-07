#!/usr/bin/env python3
"""
Test script for dimension normalization.

This script tests the normalization of dimensions for API compatibility.
"""

import sys
import json
import argparse
import logging
from pathlib import Path

# Add the project root directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# Import the module
from backend.llm.entity_type_generator import normalize_dimensions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Test the dimension normalization function')
    
    parser.add_argument('--input', '-i', 
                        type=str, 
                        required=True,
                        help='Path to input JSON file with dimensions')
    
    parser.add_argument('--output', '-o',
                        type=str, 
                        default='normalized_dimensions.json',
                        help='Path to save the normalized dimensions (default: normalized_dimensions.json)')
    
    return parser.parse_args()


def main():
    """Main function to run the normalization test."""
    args = parse_args()
    
    try:
        # Read the input dimensions
        with open(args.input, 'r') as f:
            data = json.load(f)
        
        # Extract dimensions from the response structure if needed
        if 'data' in data and 'dimensions' in data['data']:
            dimensions = data['data']['dimensions']
        elif 'dimensions' in data:
            dimensions = data['dimensions']
        else:
            dimensions = data
        
        logger.info(f"Loaded {len(dimensions)} dimensions from {args.input}")
        
        # Print the original dimensions structure
        logger.info("Original dimension structure example:")
        if dimensions:
            example = dimensions[0]
            logger.info(json.dumps(example, indent=2))
        
        # Normalize the dimensions
        normalized = normalize_dimensions(dimensions)
        
        logger.info(f"Normalized {len(normalized)} dimensions")
        
        # Print the normalized dimensions structure
        logger.info("Normalized dimension structure example:")
        if normalized:
            example = normalized[0]
            logger.info(json.dumps(example, indent=2))
        
        # Compare dimensions before and after
        for i, (orig, norm) in enumerate(zip(dimensions, normalized)):
            diff = set(norm.keys()) - set(orig.keys())
            if diff:
                logger.info(f"Dimension {i+1} ({norm.get('name')}): Added fields {diff}")
        
        # Save the normalized dimensions
        with open(args.output, 'w') as f:
            json.dump(normalized, f, indent=2)
        
        logger.info(f"Saved normalized dimensions to {args.output}")
        
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main() 