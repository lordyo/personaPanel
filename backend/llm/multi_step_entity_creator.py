#!/usr/bin/env python3
"""
Multi-Step Entity Creator using DSPy with dynamic signatures.

This module implements a two-step approach to entity generation:
1. First LLM call: Generate text dimensions based on non-text dimensions
2. Second LLM call: Generate name and backstory with all dimensions + bisociative fuel

This approach ensures higher inter-entity variance by providing random
"bisociative fuel" words to influence name generation.
"""

import os
import sys
import json
import random
import argparse
import traceback
import re
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get the repository root directory (assuming backend is one level below root)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_DIR = os.path.join(ROOT_DIR, "config")

# Define config file paths
LLM_CONFIG_PATH = os.path.join(CONFIG_DIR, "llm_settings.json")
ENTITY_CONFIG_PATH = os.path.join(CONFIG_DIR, "entity_creator.json")
BISOCIATIVE_WORDS_PATH = os.path.join(CONFIG_DIR, "bisociative_words.json")

# Load environment variables (as fallbacks)
load_dotenv()

# Import DSPy
import dspy

# Import functions from simple entity creator (using relative import)
from .simple_entity_creator import (
    load_config, 
    setup_dspy, 
    generate_dimension_values, 
    list_entities,
    get_entity_by_name, 
    get_entity_by_index, 
    get_default_entity
)


def get_random_bisociative_words(count=2):
    """Get random words for bisociative fuel from the word list."""
    try:
        with open(BISOCIATIVE_WORDS_PATH, 'r') as f:
            word_data = json.load(f)
            words = word_data.get("words", [])
            
        if not words:
            # Fallback if no words or file not found
            fallback_words = ["ocean", "mountain", "forest", "river", "tiger", 
                              "eagle", "castle", "knight", "diamond", "music",
                              "sunset", "horizon", "mystery", "adventure", "journey",
                              "laughter", "whisper", "thunder", "shadow", "spark"]
            return random.sample(fallback_words, min(count, len(fallback_words)))
            
        return random.sample(words, min(count, len(words)))
    except Exception as e:
        print(f"Error getting bisociative words: {str(e)}")
        # Return some default words if there's an error
        return ["creativity", "inspiration"]


def identify_text_dimensions(dimensions: List[Dict]) -> List[Dict]:
    """Identify text dimensions from a list of dimensions."""
    return [dim for dim in dimensions if dim.get('type') == 'text']


def create_text_dimension_signature(entity_type: str, entity_description: str, 
                                  dimensions: List[Dict], text_dimensions: List[Dict]):
    """Create a dynamically constructed Signature class for text dimension generation.
    
    Args:
        entity_type: The type of entity
        entity_description: Description of the entity type
        dimensions: List of all dimension dictionaries 
        text_dimensions: List of text dimension dictionaries
        
    Returns:
        A new DSPy Signature class for text dimension generation
    """
    attributes = {
        "__doc__": f"""
        Generate text dimensions for a {entity_type} based on its non-text attributes.
        """,
        
        # Standard input fields
        "entity_type": dspy.InputField(desc=f"The entity type ({entity_type})."),
        "entity_description": dspy.InputField(desc=f"Description of the entity type: {entity_description}"),
        "variability": dspy.InputField(desc="The level of creativity to use (0=typical, 0.5=distinct, 1=unusual)")
    }
    
    # Add non-text dimensions as input fields
    for dim in dimensions:
        # Skip text dimensions - these are what we're generating
        if dim.get('type') == 'text':
            continue
            
        field_name = f"dim_{dim['name']}"
        field_desc = dim.get('description', f"The {dim['name']} of this entity")
        
        # Add specific context based on dimension type
        if dim['type'] == 'categorical' and 'options' in dim:
            options_str = ", ".join(dim['options'])
            field_desc += f" (one of: {options_str})"
        elif dim['type'] in ['numerical', 'int', 'float'] and 'min_value' in dim and 'max_value' in dim:
            field_desc += f" (between {dim['min_value']} and {dim['max_value']})"
        elif dim['type'] == 'boolean':
            field_desc += " (true or false)"
            
        # Add to attributes dictionary
        attributes[field_name] = dspy.InputField(desc=field_desc)
    
    # Add text dimensions as output fields
    for dim in text_dimensions:
        field_name = dim.get('name', '')
        field_desc = dim.get('description', f"The {field_name} of this entity")
        
        # Add as output field
        attributes[field_name] = dspy.OutputField(desc=field_desc)
    
    # Create the class dynamically
    return type('TextDimensionGenerationSignature', (dspy.Signature,), attributes)


def create_final_entity_signature(entity_type: str, entity_description: str, 
                                dimensions: List[Dict], output_fields: List[Dict] = None):
    """Create a dynamically constructed Signature class for final name and backstory generation.
    
    Args:
        entity_type: The type of entity
        entity_description: Description of the entity type
        dimensions: List of dimension dictionaries defining input attributes
        output_fields: List of additional output field dictionaries (optional)
        
    Returns:
        A new DSPy Signature class for name and backstory generation
    """
    attributes = {
        "__doc__": f"""
        Generate a name and backstory for a {entity_type} based on all its attributes
        and the provided bisociative fuel words for creativity.
        """,
        
        # Standard input fields
        "entity_type": dspy.InputField(desc=f"The entity type."),
        "entity_description": dspy.InputField(desc=f"Description of the entity type."),
        "variability": dspy.InputField(desc="The level of creativity to use (0=typical, 0.5=distinct, 1=unusual)"),
        "bisociative_fuel": dspy.InputField(desc="Two random words to inspire creative naming and narration elements."),
        
        # Standard output fields - always present
        "name": dspy.OutputField(desc="A fitting name for this entity, inspired by its attributes and the bisociative fuel words."),
        "backstory": dspy.OutputField(desc="A cohesive description of the entity that reflects all provided attributes.")
    }
    
    # Add all dimensions as input fields
    for dim in dimensions:
        field_name = f"dim_{dim['name']}"
        field_desc = dim.get('description', f"The {dim['name']} of this entity")
        
        # Add specific context based on dimension type
        if dim['type'] == 'categorical' and 'options' in dim:
            options_str = ", ".join(dim['options'])
            field_desc += f" (one of: {options_str})"
        elif dim['type'] in ['numerical', 'int', 'float'] and 'min_value' in dim and 'max_value' in dim:
            field_desc += f" (between {dim['min_value']} and {dim['max_value']})"
        elif dim['type'] == 'boolean':
            field_desc += " (true or false)"
        elif dim['type'] == 'text':
            field_desc += " (text dimension)"
            
        # Add to attributes dictionary
        attributes[field_name] = dspy.InputField(desc=field_desc)
    
    # Add additional output fields if specified
    if output_fields:
        for field in output_fields:
            field_name = field.get('name', '')
            field_desc = field.get('description', f"The {field_name} of this entity")
            
            # Skip if the field is already defined (name, backstory)
            if field_name in ['name', 'backstory']:
                continue
                
            # Add output field
            attributes[field_name] = dspy.OutputField(desc=field_desc)
    
    # Create the class dynamically
    return type('FinalEntitySignature', (dspy.Signature,), attributes)


class MultiStepEntityCreator(dspy.Module):
    """Multi-step entity creation with optional text dimension step and final name/backstory step."""
    
    def __init__(self):
        super().__init__()
        # We'll create the predictors dynamically for each entity type
    
    def format_dimension_value(self, value):
        """Format a dimension value for display."""
        if isinstance(value, bool):
            return "Yes" if value else "No"
        return str(value)
    
    def forward(self, entity_type, entity_description, dimensions, variability=0.5, 
                dimension_values=None, output_fields=None, bisociative_words=None):
        """Generate an entity using the multi-step approach.
        
        Args:
            entity_type: The type of entity to create
            entity_description: Description of the entity
            dimensions: List of dimension definitions
            variability: Level of creativity (0=typical, 0.5=distinct, 1=unique)
            dimension_values: Dictionary of predefined dimension values (optional)
            output_fields: List of additional output fields to generate (optional)
            bisociative_words: List of words to use as bisociative fuel (if None, random words will be selected)
        
        Returns:
            An EntityResult object with name, backstory, and additional fields
        """
        # Step 1: Offline random dimension generation (for non-text dimensions)
        if dimension_values is None:
            dimension_values = generate_dimension_values(dimensions)
        
        # Print the initial dimension values
        print("\nInitial dimension values (non-text only):")
        for dim in dimensions:
            if dim['name'] in dimension_values:
                print(f"  - {dim['name']}: {self.format_dimension_value(dimension_values[dim['name']])}")
        
        # Identify text dimensions that need to be generated
        text_dimensions = identify_text_dimensions(dimensions)
        
        # Step 2: Generate text dimensions if there are any
        if text_dimensions:
            print(f"\nGenerating {len(text_dimensions)} text dimensions...")
            
            # Create text dimension signature
            TextDimensionSignature = create_text_dimension_signature(
                entity_type, 
                entity_description, 
                dimensions, 
                text_dimensions
            )
            
            # Create a predictor for text dimensions
            text_predictor = dspy.Predict(TextDimensionSignature)
            
            # Build input arguments for the text dimension prediction
            text_input_args = {
                "entity_type": entity_type,
                "entity_description": entity_description,
                "variability": variability
            }
            
            # Add non-text dimension values as input arguments
            for dim in dimensions:
                if dim.get('type') != 'text' and dim['name'] in dimension_values:
                    text_input_args[f"dim_{dim['name']}"] = dimension_values[dim['name']]
            
            # Make the prediction to generate text dimensions
            print("\nSending query for text dimensions with parameters:")
            for key, value in text_input_args.items():
                print(f"  - {key}: {value}")
                
            text_result = text_predictor(**text_input_args)
            
            # Extract and add text dimension values to the dimension_values dictionary
            for dim in text_dimensions:
                dim_name = dim.get('name', '')
                if hasattr(text_result, dim_name):
                    text_value = getattr(text_result, dim_name)
                    dimension_values[dim_name] = text_value
                    print(f"  Generated text dimension '{dim_name}': {text_value}")
        
        # Step 3: Generate the final name and backstory
        # Get or generate bisociative fuel words
        if not bisociative_words:
            bisociative_words = get_random_bisociative_words(2)
        bisociative_fuel = ", ".join(bisociative_words)
        
        print(f"\nUsing bisociative fuel: '{bisociative_fuel}'")
        
        # Create final entity signature
        FinalEntitySignature = create_final_entity_signature(
            entity_type, 
            entity_description, 
            dimensions, 
            output_fields
        )
        
        # Create a predictor for the final entity
        final_predictor = dspy.Predict(FinalEntitySignature)
        
        # Build input arguments for the final prediction
        final_input_args = {
            "entity_type": entity_type,
            "entity_description": entity_description,
            "variability": variability,
            "bisociative_fuel": bisociative_fuel
        }
        
        # Add all dimension values (both non-text and text) as input arguments
        for dim in dimensions:
            if dim['name'] in dimension_values:
                final_input_args[f"dim_{dim['name']}"] = dimension_values[dim['name']]
        
        # Debug info
        print("\nSending query for final entity with parameters:")
        for key, value in final_input_args.items():
            print(f"  - {key}: {value}")
        
        if output_fields:
            print("\nRequesting additional output fields:")
            for field in output_fields:
                print(f"  - {field.get('name')}: {field.get('description')}")
        
        # Make the prediction for the final entity
        final_result = final_predictor(**final_input_args)
        
        # Create structured result
        class EntityResult:
            def __init__(self, name, backstory, additional_fields=None, dimensions=None):
                self.name = name
                self.backstory = backstory
                self.dimension_values = dimensions or {}
                
                # Add any additional fields
                if additional_fields:
                    for field_name, field_value in additional_fields.items():
                        setattr(self, field_name, field_value)
        
        # Extract name and backstory
        name = None
        backstory = None
        additional_fields = {}
        
        if hasattr(final_result, 'name'):
            name = final_result.name
        elif hasattr(final_result, 'output') and isinstance(final_result.output, dict) and 'name' in final_result.output:
            name = final_result.output['name']
        
        if hasattr(final_result, 'backstory'):
            backstory = final_result.backstory
        elif hasattr(final_result, 'output') and isinstance(final_result.output, dict) and 'backstory' in final_result.output:
            backstory = final_result.output['backstory']
        
        # Extract additional output fields if any
        if output_fields:
            for field in output_fields:
                field_name = field.get('name')
                if hasattr(final_result, field_name):
                    additional_fields[field_name] = getattr(final_result, field_name)
                elif hasattr(final_result, 'output') and isinstance(final_result.output, dict) and field_name in final_result.output:
                    additional_fields[field_name] = final_result.output[field_name]
        
        # Fallback extraction if needed
        if name is None or backstory is None:
            # Try to parse from result text if possible
            if hasattr(final_result, 'output') and isinstance(final_result.output, str):
                # Try to extract name and backstory from the text
                text = final_result.output
                
                # Simple heuristic extraction
                name_match = re.search(r"Name:(.*?)(?:\n|$)", text)
                if name_match:
                    name = name_match.group(1).strip()
                else:
                    name = f"Unnamed {entity_type}"
                    
                backstory_match = re.search(r"Backstory:(.*?)(?:\n|$)", text, re.DOTALL)
                if backstory_match:
                    backstory = backstory_match.group(1).strip()
                else:
                    backstory = text
                
                # Try to extract additional fields
                if output_fields:
                    for field in output_fields:
                        field_name = field.get('name')
                        field_match = re.search(f"{field_name}:(.*?)(?:\n|$)", text, re.IGNORECASE | re.DOTALL)
                        if field_match:
                            additional_fields[field_name] = field_match.group(1).strip()
        
        return EntityResult(
            name=name or f"Unnamed {entity_type}",
            backstory=backstory or f"No backstory generated for this {entity_type}.",
            additional_fields=additional_fields,
            dimensions=dimension_values
        )

    async def generate_entity_async(self, entity_type, entity_description, dimensions, 
                                    variability=0.5, dimension_values=None, 
                                    output_fields=None, bisociative_words=None):
        """Async version of the entity generation function for parallel processing."""
        # This function mostly mirrors the forward method but is designed for async use
        
        # Step 1: Offline random dimension generation (if not provided)
        if dimension_values is None:
            dimension_values = generate_dimension_values(dimensions)
        
        # Identify text dimensions that need to be generated
        text_dimensions = identify_text_dimensions(dimensions)
        
        # Step 2: Generate text dimensions if there are any
        if text_dimensions:
            # Create text dimension signature
            TextDimensionSignature = create_text_dimension_signature(
                entity_type, 
                entity_description, 
                dimensions, 
                text_dimensions
            )
            
            # Create a predictor for text dimensions
            text_predictor = dspy.Predict(TextDimensionSignature)
            
            # Build input arguments for the text dimension prediction
            text_input_args = {
                "entity_type": entity_type,
                "entity_description": entity_description,
                "variability": variability
            }
            
            # Add non-text dimension values as input arguments
            for dim in dimensions:
                if dim.get('type') != 'text' and dim['name'] in dimension_values:
                    text_input_args[f"dim_{dim['name']}"] = dimension_values[dim['name']]
            
            # Make the prediction to generate text dimensions
            # Use an event loop to run the synchronous predictor call
            loop = asyncio.get_event_loop()
            text_result = await loop.run_in_executor(
                None, 
                lambda: text_predictor(**text_input_args)
            )
            
            # Extract and add text dimension values to the dimension_values dictionary
            for dim in text_dimensions:
                dim_name = dim.get('name', '')
                if hasattr(text_result, dim_name):
                    dimension_values[dim_name] = getattr(text_result, dim_name)
        
        # Step 3: Generate the final name and backstory
        # Get or generate bisociative fuel words
        if not bisociative_words:
            bisociative_words = get_random_bisociative_words(2)
        bisociative_fuel = ", ".join(bisociative_words)
        
        # Create final entity signature
        FinalEntitySignature = create_final_entity_signature(
            entity_type, 
            entity_description, 
            dimensions, 
            output_fields
        )
        
        # Create a predictor for the final entity
        final_predictor = dspy.Predict(FinalEntitySignature)
        
        # Build input arguments for the final prediction
        final_input_args = {
            "entity_type": entity_type,
            "entity_description": entity_description,
            "variability": variability,
            "bisociative_fuel": bisociative_fuel
        }
        
        # Add all dimension values as input arguments
        for dim in dimensions:
            if dim['name'] in dimension_values:
                final_input_args[f"dim_{dim['name']}"] = dimension_values[dim['name']]
        
        # Make the prediction for the final entity
        loop = asyncio.get_event_loop()
        final_result = await loop.run_in_executor(
            None, 
            lambda: final_predictor(**final_input_args)
        )
        
        # Extract and return the output in the expected format
        class EntityResult:
            def __init__(self, name, backstory, additional_fields=None, dimensions=None):
                self.name = name
                self.backstory = backstory
                self.dimension_values = dimensions or {}
                
                # Add any additional fields
                if additional_fields:
                    for field_name, field_value in additional_fields.items():
                        setattr(self, field_name, field_value)
        
        # Process results (same as in forward method)
        name = None
        backstory = None
        additional_fields = {}
        
        if hasattr(final_result, 'name'):
            name = final_result.name
        elif hasattr(final_result, 'output') and isinstance(final_result.output, dict) and 'name' in final_result.output:
            name = final_result.output['name']
        
        if hasattr(final_result, 'backstory'):
            backstory = final_result.backstory
        elif hasattr(final_result, 'output') and isinstance(final_result.output, dict) and 'backstory' in final_result.output:
            backstory = final_result.output['backstory']
        
        # Extract additional output fields if any
        if output_fields:
            for field in output_fields:
                field_name = field.get('name')
                if hasattr(final_result, field_name):
                    additional_fields[field_name] = getattr(final_result, field_name)
                elif hasattr(final_result, 'output') and isinstance(final_result.output, dict) and field_name in final_result.output:
                    additional_fields[field_name] = final_result.output[field_name]
        
        # Create a simple fallback if needed
        if name is None or backstory is None:
            # Try to parse from result text if possible
            if hasattr(final_result, 'output') and isinstance(final_result.output, str):
                # Try to extract name and backstory from the text
                text = final_result.output
                
                # Simple heuristic extraction
                name_match = re.search(r"Name:(.*?)(?:\n|$)", text)
                if name_match:
                    name = name_match.group(1).strip()
                else:
                    name = f"Unnamed {entity_type}"
                    
                backstory_match = re.search(r"Backstory:(.*?)(?:\n|$)", text, re.DOTALL)
                if backstory_match:
                    backstory = backstory_match.group(1).strip()
                else:
                    backstory = text
                
                # Try to extract additional fields
                if output_fields:
                    for field in output_fields:
                        field_name = field.get('name')
                        field_match = re.search(f"{field_name}:(.*?)(?:\n|$)", text, re.IGNORECASE | re.DOTALL)
                        if field_match:
                            additional_fields[field_name] = field_match.group(1).strip()
        
        return EntityResult(
            name=name or f"Unnamed {entity_type}",
            backstory=backstory or f"No backstory generated for this {entity_type}.",
            additional_fields=additional_fields,
            dimensions=dimension_values
        )


async def generate_entities_parallel(creator, entity_type, entity_description, dimensions, 
                                    variability, output_fields, num_entities, max_parallel=50):
    """Generate multiple entities in parallel with a limit on concurrent operations."""
    # Create a semaphore to limit the number of concurrent calls
    semaphore = asyncio.Semaphore(max_parallel)
    
    # Create a list to store the tasks
    tasks = []
    
    # Define a wrapper function that respects the semaphore
    async def generate_with_semaphore(i):
        async with semaphore:
            # Generate random dimension values for this entity
            dimension_values = generate_dimension_values(dimensions)
            
            # Generate random bisociative words for this entity
            bisociative_words = get_random_bisociative_words(2)
            
            # Print progress information
            print(f"\n--- Generating entity {i+1} of {num_entities} ---")
            print(f"Using bisociative words: {', '.join(bisociative_words)}")
            
            # Generate the entity
            try:
                entity = await creator.generate_entity_async(
                    entity_type, 
                    entity_description, 
                    dimensions, 
                    variability, 
                    dimension_values,
                    output_fields,
                    bisociative_words
                )
                print(f"Created: {entity.name}")
                return entity
            except Exception as e:
                print(f"Error generating entity {i+1}: {str(e)}")
                # Return a placeholder entity on error
                class ErrorEntity:
                    def __init__(self):
                        self.name = f"Error Entity {i+1}"
                        self.backstory = f"This entity could not be generated due to an error: {str(e)}"
                        self.dimension_values = dimension_values
                return ErrorEntity()
    
    # Create tasks for all entities
    for i in range(num_entities):
        tasks.append(generate_with_semaphore(i))
    
    # Run all tasks concurrently and gather results
    return await asyncio.gather(*tasks)


def main():
    """Run entity generation with the multi-step approach."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate an entity using the multi-step DSPy approach")
    parser.add_argument("--list", action="store_true", help="List available entity templates")
    parser.add_argument("--entity", type=str, help="Entity template name to use")
    parser.add_argument("--index", type=int, help="Entity template index to use (1-based)")
    parser.add_argument("--show-dimensions", action="store_true", help="Show dimensions for the selected entity")
    parser.add_argument("--count", "-n", type=int, help="Number of entities to generate")
    parser.add_argument("--max-parallel", "-p", type=int, default=50, help="Maximum number of parallel generation calls")
    parser.add_argument("--words", type=str, help="Comma-separated bisociative words to use (overrides random selection)")
    args = parser.parse_args()
    
    # Load configuration
    llm_config = load_config(LLM_CONFIG_PATH, "LLM")
    entity_config = load_config(ENTITY_CONFIG_PATH, "Entity")
    
    # Just list entities and exit if requested
    if args.list:
        list_entities(entity_config)
        return
    
    # Get entity parameters from config
    entity_params = None
    if args.entity:
        entity_params = get_entity_by_name(entity_config, args.entity)
        if not entity_params:
            print(f"Error: Entity '{args.entity}' not found in config")
            list_entities(entity_config)
            sys.exit(1)
    elif args.index:
        entity_params = get_entity_by_index(entity_config, args.index)
        if not entity_params:
            print(f"Error: Entity index {args.index} not found in config")
            list_entities(entity_config)
            sys.exit(1)
    else:
        entity_params = get_default_entity(entity_config)
    
    # Just show dimensions and exit if requested
    if args.show_dimensions:
        print(f"\nDimensions for {entity_params.get('name', 'Unnamed Template')} ({entity_params.get('entity_type')}):")
        print("-" * 40)
        dimensions = entity_params.get("dimensions", [])
        if not dimensions:
            print("No dimensions defined")
        else:
            for i, dim in enumerate(dimensions, 1):
                dim_type = dim.get('type', 'unknown')
                type_info = ""
                
                if dim_type == 'categorical' and 'options' in dim:
                    type_info = f"Options: {', '.join(dim['options'])}"
                elif dim_type in ['numerical', 'int', 'float'] and 'min_value' in dim and 'max_value' in dim:
                    type_info = f"Range: {dim['min_value']} to {dim['max_value']}"
                
                print(f"{i}. {dim.get('name')}: {dim.get('description')} ({dim_type}) {type_info}")
        return
    
    # Configure DSPy
    if not setup_dspy(llm_config):
        sys.exit(1)
    
    # Determine how many entities to generate
    num_entities = args.count if args.count is not None else entity_config.get("num_entities", 1)
    max_parallel = min(args.max_parallel, 50)  # Limit to 50 max as requested
    
    # Process any manually specified bisociative words
    bisociative_words = None
    if args.words:
        bisociative_words = [word.strip() for word in args.words.split(',')]
        print(f"Using specified bisociative words: {', '.join(bisociative_words)}")
    
    # Create the multi-step module
    creator = MultiStepEntityCreator()
    
    # Extract parameters
    entity_type = entity_params.get("entity_type")
    entity_description = entity_params.get("entity_description")
    variability = entity_params.get("variability", 0.5)
    entity_name = entity_params.get("name", "Unnamed Template")
    dimensions = entity_params.get("dimensions", [])
    output_fields = entity_params.get("output_fields", [])
    
    # Generate the entities
    print(f"\nUsing template: {entity_name}")
    print(f"Generating {num_entities} {entity_type}(s) with variability {variability} and {len(dimensions)} dimensions...")
    print(f"Using multi-step generation with bisociative fueling")
    print(f"Using parallel processing with max {max_parallel} concurrent calls")
    
    # Count text dimensions
    text_dimensions = identify_text_dimensions(dimensions)
    print(f"Found {len(text_dimensions)} text dimensions that will be generated in step 1")
    
    if output_fields:
        print(f"Including {len(output_fields)} additional output fields")
    
    try:
        # If just generating one entity, use the synchronous method
        if num_entities == 1:
            # Get specific bisociative words if provided, otherwise random
            words_to_use = bisociative_words if bisociative_words else get_random_bisociative_words(2)
            
            print(f"\nUsing bisociative words: {', '.join(words_to_use)}")
            entity = creator.forward(
                entity_type, 
                entity_description, 
                dimensions, 
                variability, 
                None,  # dimension_values - will be generated
                output_fields,
                words_to_use
            )
            
            # Print entity details
            print("\n" + "="*50)
            print(f"GENERATED {entity_type.upper()}")
            print("="*50)
            
            print(f"\nName: {entity.name}")
            print("-" * 50)
            
            # Print backstory
            print(f"Backstory:")
            print(f"{entity.backstory}")
            
            # Print dimension values
            print("\nDimension values:")
            for dim in dimensions:
                if dim['name'] in entity.dimension_values:
                    value = entity.dimension_values[dim['name']]
                    formatted_value = "Yes" if isinstance(value, bool) and value else "No" if isinstance(value, bool) else str(value)
                    print(f"  - {dim['name']}: {formatted_value}")
            
            # Print any additional generated fields
            for field_name in dir(entity):
                # Skip standard attributes and private/special attributes
                if field_name in ['name', 'backstory', 'dimension_values'] or field_name.startswith('_'):
                    continue
                    
                print(f"\n{field_name.capitalize()}:")
                print(f"{getattr(entity, field_name)}")
        else:
            # Run the async function to generate entities in parallel
            if sys.platform == 'win32':
                # Windows requires a specific event loop policy
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
            loop = asyncio.get_event_loop()
            generated_entities = loop.run_until_complete(
                generate_entities_parallel(
                    creator, 
                    entity_type, 
                    entity_description, 
                    dimensions, 
                    variability, 
                    output_fields, 
                    num_entities,
                    max_parallel
                )
            )
            
            # After generating all entities, print detailed information
            print("\n" + "="*50)
            print(f"GENERATED {num_entities} {entity_type.upper()}(S)")
            print("="*50)
            
            for i, entity in enumerate(generated_entities, 1):
                print(f"\nENTITY {i}: {entity.name}")
                print("-" * 50)
                
                # Print backstory
                print(f"Backstory:")
                print(f"{entity.backstory}")
                
                # Print any additional generated fields
                for field_name in dir(entity):
                    # Skip standard attributes and private/special attributes
                    if field_name in ['name', 'backstory', 'dimension_values'] or field_name.startswith('_'):
                        continue
                        
                    print(f"\n{field_name.capitalize()}:")
                    print(f"{getattr(entity, field_name)}")
                    
                print("-" * 50)
        
        print("\nGeneration complete!")
        
    except Exception as e:
        print(f"Error during generation: {e}")
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main() 