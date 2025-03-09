#!/usr/bin/env python3
"""
Direct test of the batch entity creator functionality without Flask.

This script tests the batch entity creator directly to verify that it's working properly.
"""

import os
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the batch entity creator
from batch_entity_creator import BatchEntityCreator, setup_dspy

async def main():
    """Test the batch entity creator directly."""
    print("Setting up DSPy...")
    # Try to set up DSPy with an empty config (will use environment variables)
    if not setup_dspy({}):
        print("Failed to set up DSPy")
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
    
    # Generate a small batch of entities
    batch_size = 2
    print(f"Generating {batch_size} {entity_type} entities...")
    
    try:
        entities = await creator.generate_batch_async(
            entity_type=entity_type,
            entity_description=entity_description,
            dimensions=dimensions,
            variability=0.7,
            batch_size=batch_size,
            output_fields=output_fields
        )
        
        # Format into JSON structure
        result = {
            "status": "success",
            "entities": []
        }
        
        for i, entity in enumerate(entities):
            entity_data = {
                "id": f"{entity_type}_{i+1}",
                "name": entity.name,
                "backstory": entity.backstory,
                "dimensions": {}
            }
            
            # Add dimension values
            for dim in dimensions:
                if dim["name"] in entity.dimension_values:
                    entity_data["dimensions"][dim["name"]] = entity.dimension_values[dim["name"]]
            
            # Add additional fields
            for field in output_fields:
                field_name = field.get("name")
                if hasattr(entity, field_name):
                    entity_data[field_name] = getattr(entity, field_name)
            
            result["entities"].append(entity_data)
        
        # Display the results
        print(f"\nGenerated {len(entities)} entities:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error generating entities: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main()) 