#!/usr/bin/env python3
"""
Direct test of the batch entity creator

This script tests the batch entity creator directly without going through the Flask API.
"""

import os
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the batch entity creator directly
from llm.batch_entity_creator import (
    BatchEntityCreator,
    load_config,
    setup_dspy,
    MAX_PARALLEL_ENTITIES
)

async def test_batch_creation():
    """Test the batch entity creator functionality directly."""
    # Load LLM configuration
    llm_config = load_config("config/llm_config.json", "LLM")
    
    # Set up DSPy
    if not setup_dspy(llm_config):
        print("Failed to set up DSPy. Exiting.")
        return
    
    # Create a test entity configuration
    entity_config = {
        "type": "character",
        "description": "A fictional character for a fantasy RPG game",
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
        ]
    }
    
    # Extract entity details
    entity_type = entity_config["type"]
    entity_description = entity_config["description"]
    dimensions = entity_config["dimensions"]
    output_fields = entity_config["output_fields"]
    
    print(f"Creating batch entity creator...")
    creator = BatchEntityCreator()
    
    # Generate a small batch of entities for testing
    batch_size = 2
    print(f"Generating {batch_size} {entity_type} entities...")
    
    entities = await creator.generate_batch_async(
        entity_type=entity_type,
        entity_description=entity_description,
        dimensions=dimensions,
        variability=0.7,
        batch_size=batch_size,
        output_fields=output_fields
    )
    
    # Display the results
    print(f"\nGenerated {len(entities)} entities:")
    for i, entity in enumerate(entities):
        print(f"\n--- Entity {i+1}: {entity.name} ---")
        print(f"Backstory: {entity.backstory}")
        
        # Print additional fields
        for field in output_fields:
            field_name = field.get("name")
            if hasattr(entity, field_name):
                print(f"{field_name.capitalize()}: {getattr(entity, field_name)}")
        
        # Print dimension values
        print("\nDimension values:")
        for dim in dimensions:
            if dim['name'] in entity.dimension_values:
                value = entity.dimension_values[dim['name']]
                print(f"  - {dim['name']}: {value}")

if __name__ == "__main__":
    asyncio.run(test_batch_creation()) 