#!/usr/bin/env python3
"""
Simple test script for DSPy entity type dimensions generation.

This script tests the functionality of generating entity type dimensions using DSPy directly.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv
import dspy
from typing import Dict, List, Any

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Define the DSPy signature
class EntityTypeDimensionsSignature(dspy.Signature):
    """Generate dimensions for an entity type based on name and description."""
    
    entity_type_name: str = dspy.InputField(
        desc="The name of the entity type to generate dimensions for"
    )
    entity_type_description: str = dspy.InputField(
        desc="A detailed description of the entity type, explaining what it represents"
    )
    n_dimensions: int = dspy.InputField(
        desc="Number of dimensions to create for this entity type"
    )
    
    dimensions: List[Dict[str, Any]] = dspy.OutputField(
        desc="""JSON list of dimensions, where each dimension has:
        - name: The name of the dimension
        - description: A description of what this dimension represents
        - type: The type of dimension (boolean, categorical, int, float, text)
        - options: List of options for categorical dimensions (only for categorical type)
        - min_value: Minimum value for int/float dimensions (only for int/float types)
        - max_value: Maximum value for int/float dimensions (only for int/float types)
        - distribution: Distribution type for int/float dimensions ("uniform", "normal", "skewed") 
                       or percentage for boolean ("percentage")
        """
    )


def setup_dspy():
    """Set up DSPy with configuration from environment variables."""
    # Get the API key from environment variable
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set")

    # Configure DSPy with OpenAI
    model_name = os.environ.get('DSPY_MODEL', 'gpt-4o-mini')
    
    # Create the language model using dspy.LM
    lm = dspy.LM(f'openai/{model_name}', 
                api_key=api_key,
                temperature=0.7,
                max_tokens=2000)
    
    logger.info(f"Configuring DSPy with model: {model_name}")
    dspy.configure(lm=lm)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Test entity type dimensions generation')
    
    parser.add_argument('--input', '-i', 
                        type=str, 
                        help='Path to input JSON file with entity type information')
    
    parser.add_argument('--output', '-o',
                        type=str, 
                        default='entity_type_dimensions.json',
                        help='Path to save the generated dimensions (default: entity_type_dimensions.json)')
    
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
    """Main function to run the entity type dimensions generator test."""
    args = parse_args()
    
    # Set up DSPy
    setup_dspy()
    
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
    if not entity_type_name or not entity_type_description:
        logger.error("Entity type name and description are required")
        return
    
    logger.info(f"Generating dimensions for entity type: {entity_type_name}")
    logger.info(f"Description: {entity_type_description}")
    logger.info(f"Number of dimensions: {n_dimensions}")
    
    # Create the DSPy predictor
    generator = dspy.ChainOfThought(EntityTypeDimensionsSignature)
    
    try:
        # Generate dimensions
        prediction = generator(
            entity_type_name=entity_type_name,
            entity_type_description=entity_type_description,
            n_dimensions=n_dimensions
        )
        
        # Extract dimensions from prediction
        dimensions = prediction.dimensions
        
        # Validate the dimensions format
        if not isinstance(dimensions, list):
            logger.error(f"Invalid dimensions format: {dimensions}")
            raise ValueError("Generated dimensions are not in list format")
        
        # Print the generated dimensions
        logger.info(f"Generated {len(dimensions)} dimensions:")
        for i, dim in enumerate(dimensions, 1):
            logger.info(f"Dimension {i}: {dim.get('name')} ({dim.get('type')})")
        
        # Save the dimensions to the output file
        with open(args.output, 'w') as f:
            json.dump(dimensions, f, indent=2)
        
        logger.info(f"Saved dimensions to {args.output}")
        
    except Exception as e:
        logger.error(f"Error generating dimensions: {e}")


if __name__ == "__main__":
    main() 