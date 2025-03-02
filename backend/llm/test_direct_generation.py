#!/usr/bin/env python3
import sys
import os
import json
import traceback
from pprint import pprint

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import necessary modules
import dspy
from llm.dspy_modules import EntityGenerator, LLMError, create_entity_signature

def test_direct_entity_generation():
    """
    Test function to generate an entity using EntityGenerator with hardcoded data
    instead of fetching from the database.
    """
    # Hardcoded entity type
    entity_type = "Fantasy Character"
    
    # Hardcoded entity description
    entity_description = "A mysterious character from a fantasy novel with magical abilities."
    
    # Hardcoded dimensions - this would normally come from the database
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
            "name": "magicType",
            "type": "categorical",
            "description": "Type of magic used",
            "options": ["Elemental", "Arcane", "Divine", "Wild", "Necromancy", "None"]
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
    
    # Hardcoded variability level (low, medium, high)
    variability = "high"
    
    try:
        print(f"\n{'='*80}")
        print(f"TESTING DIRECT ENTITY GENERATION")
        print(f"{'='*80}")
        
        # Set up DSPy with OpenAI
        # First check if OPENAI_API_KEY is set
        if 'OPENAI_API_KEY' not in os.environ:
            print("OPENAI_API_KEY environment variable not set.")
            print("Please set it with: export OPENAI_API_KEY='your-api-key'")
            return
        
        print("Configuring DSPy with OpenAI...")
        
        # Configure DSPy with OpenAI using the modern approach
        lm = dspy.LM('openai/gpt-4o-mini')
        dspy.settings.configure(lm=lm)
        
        print(f"DSPy configured with model: openai/gpt-4o-mini")
        
        # For debugging: Try a direct LM call to see raw output
        print("\n--- TESTING DIRECT LM CALL ---")
        # Generate non-text attributes
        non_text_attributes = {}
        for dim in dimensions:
            if dim['type'] == 'numerical':
                non_text_attributes[dim['name']] = 300  # Fixed value for testing
            elif dim['type'] == 'categorical':
                non_text_attributes[dim['name']] = dim['options'][0] if 'options' in dim else None
            elif dim['type'] == 'boolean':
                non_text_attributes[dim['name']] = True
        
        # Create a signature for testing
        print("Creating signature class...")
        EntitySignature = create_entity_signature(entity_type, dimensions, non_text_attributes, variability, entity_description)
        
        print("Creating predictor...")
        predictor = dspy.Predict(EntitySignature)
        
        # Prepare input arguments
        input_args = {
            "entity_type": entity_type,
            "entity_description": entity_description,
            "variability": variability
        }
        
        for attr_name, attr_value in non_text_attributes.items():
            input_args[f"attr_{attr_name}"] = attr_value
        
        print("Input arguments:", input_args)
        
        # Make a direct prediction
        print("Making direct prediction call...")
        direct_prediction = predictor(**input_args)
        
        # Print the raw prediction
        print("\nRaw prediction result:")
        print(f"Prediction type: {type(direct_prediction)}")
        print(f"Prediction dict: {direct_prediction.toDict() if hasattr(direct_prediction, 'toDict') else 'No toDict method'}")
        print(f"Prediction keys: {direct_prediction.keys() if hasattr(direct_prediction, 'keys') else 'No keys method'}")
        
        # Continue with normal test
        print("\n--- CONTINUING WITH NORMAL TEST ---")
        generator = EntityGenerator()
        
        # Generate an entity
        print(f"\nGenerating {entity_type} with {variability} variability...")
        print(f"Entity description: {entity_description}")
        
        entity = generator.forward(
            entity_type=entity_type,
            dimensions=dimensions,
            variability=variability,
            entity_description=entity_description
        )
        
        # Print the generated entity
        print(f"\n{'='*40} GENERATED ENTITY {'='*40}\n")
        print(f"Name: {entity['name']}")
        print(f"\nDescription: {entity['description']}")
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
        print(f"\n{'='*80}")
        
    except LLMError as e:
        print(f"\nLLM Error in entity generation: {str(e)}")
    except Exception as e:
        print(f"\nError in entity generation: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_entity_generation() 