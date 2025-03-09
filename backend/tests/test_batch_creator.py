"""
Test script for batch entity creator

This script demonstrates how to use the batch entity creator to generate
multiple diverse entities in a single API call.
"""

import os
import json
import asyncio
import sys
from dotenv import load_dotenv

# Add the parent directory to sys.path to allow importing the batch_entity_creator module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.batch_entity_creator import (
    BatchEntityCreator, 
    load_config, 
    setup_dspy, 
    MAX_PARALLEL_ENTITIES
)

# Load environment variables
load_dotenv()

async def test_batch_generation():
    """Test the batch entity generation functionality."""
    # Load configuration
    llm_config = load_config("../../config/llm_config.json", "LLM")
    
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
            },
            {
                "name": "quote",
                "description": "A memorable quote or catchphrase for this character"
            }
        ]
    }
    
    # Extract entity details
    entity_type = entity_config["type"]
    entity_description = entity_config["description"]
    dimensions = entity_config["dimensions"]
    output_fields = entity_config["output_fields"]
    
    # Create batch entity creator
    creator = BatchEntityCreator()
    
    # Define batch size (smaller than MAX_PARALLEL_ENTITIES for testing)
    batch_size = min(3, MAX_PARALLEL_ENTITIES)
    
    print(f"Testing batch generation of {batch_size} {entity_type} entities...")
    print(f"Entity type: {entity_type}")
    print(f"Description: {entity_description}")
    print(f"Using {len(dimensions)} dimensions and {len(output_fields)} output fields")
    
    # Generate entities using the batch method
    entities = await creator.generate_batch_async(
        entity_type=entity_type,
        entity_description=entity_description,
        dimensions=dimensions,
        variability=0.7,  # Higher variability for more diverse results
        batch_size=batch_size,
        output_fields=output_fields
    )
    
    # Create a results structure similar to what an API would return
    api_results = {
        "status": "success",
        "entities": [],
        "metadata": {
            "entity_type": entity_type,
            "batch_size": batch_size,
            "dimensions_count": len(dimensions),
            "output_fields_count": len(output_fields)
        }
    }
    
    # Process the generated entities
    for i, entity in enumerate(entities):
        entity_data = {
            "id": f"entity_{i+1}",
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
        
        api_results["entities"].append(entity_data)
    
    # Print the results in a formatted way
    print("\n=== API Response Simulation ===\n")
    print(json.dumps(api_results, indent=2))
    
    # Print a summary for each entity
    print("\n=== Entity Summaries ===\n")
    for i, entity in enumerate(entities):
        print(f"\nEntity {i+1}: {entity.name}")
        print(f"- Alignment: {entity.dimension_values.get('alignment', 'Unknown')}")
        print(f"- Class: {entity.dimension_values.get('class', 'Unknown')}")
        print(f"- Age: {entity.dimension_values.get('age', 'Unknown')}")
        
        if hasattr(entity, 'quote'):
            print(f"- Quote: \"{entity.quote}\"")
    
    print("\n=== Test Complete ===")
    return entities

def main():
    """Main function to run the test."""
    asyncio.run(test_batch_generation())

if __name__ == "__main__":
    main() 