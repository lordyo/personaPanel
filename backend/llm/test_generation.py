#!/usr/bin/env python3
import sys
import os
import json
from pprint import pprint

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import necessary modules
from llm.dspy_modules import EntityGenerator

def test_entity_generation():
    """
    Test function to generate an entity using EntityGenerator
    """
    # Example entity type
    entity_type = "Character"
    
    # Example entity description
    entity_description = "A mysterious character from a fantasy novel with magical abilities."
    
    # Example dimensions
    dimensions = [
        {
            "name": "age",
            "type": "numerical",
            "description": "Age in years",
            "min_value": 20,
            "max_value": 500
        },
        {
            "name": "race",
            "type": "categorical",
            "description": "Fantasy race",
            "options": ["Human", "Elf", "Dwarf", "Orc", "Halfling"]
        },
        {
            "name": "hasMagic",
            "type": "boolean",
            "description": "Whether the character can use magic"
        },
        {
            "name": "backstory",
            "type": "text",
            "description": "The character's origin story and background"
        },
        {
            "name": "personality",
            "type": "text",
            "description": "Description of personality traits and character"
        },
        {
            "name": "appearance",
            "type": "text",
            "description": "Physical appearance and distinguishing features"
        }
    ]
    
    # Variability level (low, medium, high)
    variability = "high"
    
    try:
        # Create an entity generator
        generator = EntityGenerator()
        
        # Generate an entity
        print(f"Generating {entity_type} with {variability} variability...")
        print(f"Entity description: {entity_description}")
        
        entity = generator.forward(
            entity_type=entity_type,
            dimensions=dimensions,
            variability=variability,
            entity_description=entity_description
        )
        
        # Print the generated entity
        print("\n=============== GENERATED ENTITY ===============\n")
        print(f"Name: {entity['name']}")
        print(f"Description: {entity['description']}")
        print("\nAttributes:")
        for attr_name, attr_value in entity['attributes'].items():
            print(f"  {attr_name}: {attr_value}")
            
        # Save the entity to a file for reference
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'generated')
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{entity['name'].replace(' ', '_')}.json")
        with open(output_path, 'w') as f:
            json.dump(entity, f, indent=2)
            
        print(f"\nEntity saved to: {output_path}")
        
    except Exception as e:
        print(f"Error generating entity: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_entity_generation() 