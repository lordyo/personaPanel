#!/usr/bin/env python3
"""
Test script for the multi-step entity creator.

This script demonstrates how to use the multi-step approach to generate entities with 
higher inter-entity variance using random bisociative fuel words.
"""

import os
import sys
import argparse
import traceback
from typing import List

# Add backend directory to path to allow imports
BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if os.path.exists(BACKEND_DIR):
    sys.path.append(BACKEND_DIR)

# Import multi-step entity creator
try:
    from backend.llm.multi_step_entity_creator import (
        MultiStepEntityCreator,
        setup_dspy,
        load_config,
        get_entity_by_name,
        get_entity_by_index,
        get_default_entity,
        get_random_bisociative_words,
        identify_text_dimensions
    )
except ImportError as e:
    print(f"Error importing multi-step entity creator: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

# Root and config directories
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
LLM_CONFIG_PATH = os.path.join(CONFIG_DIR, "llm_settings.json")
ENTITY_CONFIG_PATH = os.path.join(CONFIG_DIR, "entity_creator.json")


def list_available_entities():
    """List all available entity templates from config."""
    entity_config = load_config(ENTITY_CONFIG_PATH, "Entity")
    entities = entity_config.get("entity_inputs", [])
    
    if not entities:
        print("No entity templates found in config")
        return
    
    print("\nAvailable entity templates:")
    print("-" * 60)
    for i, entity in enumerate(entities, 1):
        dimensions = entity.get('dimensions', [])
        text_dimensions = identify_text_dimensions(dimensions)
        text_count = len(text_dimensions)
        non_text_count = len(dimensions) - text_count
        
        print(f"{i}. {entity.get('name', 'Unnamed')} - {entity.get('entity_type')} "
              f"({non_text_count} non-text dims, {text_count} text dims)")
    print("-" * 60)


def generate_sample_entities(entity_name=None, entity_index=None, count=1, bisociative_words=None):
    """Generate sample entities using the multi-step approach."""
    # Load configuration
    llm_config = load_config(LLM_CONFIG_PATH, "LLM")
    entity_config = load_config(ENTITY_CONFIG_PATH, "Entity")
    
    # Configure DSPy
    if not setup_dspy(llm_config):
        print("Failed to set up DSPy. Check your API keys and configuration.")
        sys.exit(1)
    
    # Get entity parameters from config
    entity_params = None
    if entity_name:
        entity_params = get_entity_by_name(entity_config, entity_name)
        if not entity_params:
            print(f"Error: Entity '{entity_name}' not found in config")
            list_available_entities()
            sys.exit(1)
    elif entity_index:
        entity_params = get_entity_by_index(entity_config, entity_index)
        if not entity_params:
            print(f"Error: Entity index {entity_index} not found in config")
            list_available_entities()
            sys.exit(1)
    else:
        entity_params = get_default_entity(entity_config)
    
    # Create the multi-step module
    creator = MultiStepEntityCreator()
    
    # Extract entity parameters
    entity_type = entity_params.get("entity_type")
    entity_description = entity_params.get("entity_description")
    variability = entity_params.get("variability", 0.5)
    entity_name = entity_params.get("name", "Unnamed Template")
    dimensions = entity_params.get("dimensions", [])
    output_fields = entity_params.get("output_fields", [])
    
    # Identify text dimensions to show how many will be generated
    text_dimensions = identify_text_dimensions(dimensions)
    
    # Print entity configuration
    print(f"\nTemplate: {entity_name}")
    print(f"Type: {entity_type}")
    print(f"Description: {entity_description}")
    print(f"Variability: {variability}")
    print(f"Dimensions: {len(dimensions)} total ({len(text_dimensions)} text dimensions)")
    
    if not text_dimensions:
        print("  No text dimensions found. Only the 2-step process will be used.")
    else:
        print(f"  Text dimensions to be generated:")
        for dim in text_dimensions:
            print(f"    - {dim.get('name')}: {dim.get('description')}")
    
    if output_fields:
        print(f"Output fields: {len(output_fields)}")
        for field in output_fields:
            print(f"  - {field.get('name')}: {field.get('description')}")
    
    # Generate entities
    print(f"\nGenerating {count} {entity_type}(s) with multi-step approach...")
    
    generated_entities = []
    for i in range(count):
        try:
            # Get or generate bisociative words
            words_for_this_entity = None
            if bisociative_words and i == 0:  # Only use provided words for the first entity
                words_for_this_entity = bisociative_words
            else:
                words_for_this_entity = get_random_bisociative_words(2)
            
            print(f"\n--- Entity {i+1} of {count} ---")
            print(f"Using bisociative fuel: {', '.join(words_for_this_entity)}")
            
            entity = creator.forward(
                entity_type=entity_type,
                entity_description=entity_description,
                dimensions=dimensions,
                variability=variability,
                dimension_values=None,  # Will be randomly generated
                output_fields=output_fields,
                bisociative_words=words_for_this_entity
            )
            
            generated_entities.append(entity)
            
            # Print a summary of the generated entity
            print(f"\nCreated: {entity.name}")
            print(f"Backstory preview: {entity.backstory[:100]}...")
            
        except Exception as e:
            print(f"Error generating entity {i+1}: {str(e)}")
            print(traceback.format_exc())
    
    # Print full details of all generated entities
    if generated_entities:
        print("\n" + "="*60)
        print(f"GENERATED {len(generated_entities)} {entity_type.upper()}(S)")
        print("="*60)
        
        for i, entity in enumerate(generated_entities, 1):
            print(f"\nENTITY {i}: {entity.name}")
            print("-" * 60)
            
            # Print backstory
            print(f"Backstory:")
            print(f"{entity.backstory}")
            
            # Print dimension values
            print("\nDimension values:")
            for dim in dimensions:
                if dim['name'] in entity.dimension_values:
                    value = entity.dimension_values[dim['name']]
                    if isinstance(value, bool):
                        formatted_value = "Yes" if value else "No"
                    else:
                        formatted_value = str(value)
                    print(f"  - {dim['name']}: {formatted_value}")
            
            # Print additional fields
            for field_name in dir(entity):
                # Skip standard attributes and private/special attributes
                if field_name in ['name', 'backstory', 'dimension_values'] or field_name.startswith('_'):
                    continue
                    
                print(f"\n{field_name.capitalize()}:")
                print(f"{getattr(entity, field_name)}")
                
            print("-" * 60)
        
        print("\nGeneration complete!")
    else:
        print("\nNo entities were successfully generated.")
        

def main():
    """Run the test script with command line arguments."""
    parser = argparse.ArgumentParser(description="Test the multi-step entity generator")
    parser.add_argument("--list", action="store_true", help="List available entity templates")
    parser.add_argument("--entity", type=str, help="Entity template name to use")
    parser.add_argument("--index", type=int, help="Entity template index to use (1-based)")
    parser.add_argument("--count", "-n", type=int, default=1, help="Number of entities to generate")
    parser.add_argument("--words", type=str, help="Comma-separated bisociative words to use for the first entity")
    args = parser.parse_args()
    
    if args.list:
        list_available_entities()
        return
    
    # Process any manually specified bisociative words
    bisociative_words = None
    if args.words:
        bisociative_words = [word.strip() for word in args.words.split(',')]
    
    # Generate sample entities
    generate_sample_entities(
        entity_name=args.entity,
        entity_index=args.index,
        count=args.count,
        bisociative_words=bisociative_words
    )


if __name__ == "__main__":
    main() 