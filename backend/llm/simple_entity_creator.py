#!/usr/bin/env python3
"""
Simple Entity Creator using DSPy with dynamic signatures.

This script creates a DSPy module that takes an entity type, description, and
dynamically defined dimensions to generate a name and backstory.
"""

import os
import sys
import json
import random
import argparse
import traceback
import re
import asyncio
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get the repository root directory (assuming backend is one level below root)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_DIR = os.path.join(ROOT_DIR, "config")

# Define config file paths
LLM_CONFIG_PATH = os.path.join(CONFIG_DIR, "llm_settings.json")
ENTITY_CONFIG_PATH = os.path.join(CONFIG_DIR, "entity_creator.json")

# Load environment variables (as fallbacks)
load_dotenv()

# Import DSPy
import dspy

def load_config(config_path, config_type):
    """Load configuration from JSON file with error handling."""
    try:
        if not os.path.exists(config_path):
            print(f"Warning: {config_type} config file not found at {config_path}")
            return {}
        
        with open(config_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {config_type} config file")
        return {}
    except Exception as e:
        print(f"Error loading {config_type} config: {str(e)}")
        return {}

def setup_dspy(llm_config):
    """Configure DSPy with settings from config or environment variables."""
    # Get model settings with fallbacks to env vars
    settings = llm_config.get("model_settings", {})
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        return False
    
    # Get model name from config or env
    model_name = settings.get("model") or os.getenv("DSPY_MODEL", "gpt-4o-mini")
    
    print(f"Configuring DSPy with model: openai/{model_name}")
    try:
        # Configure with settings from config file
        lm = dspy.LM(
            f"openai/{model_name}", 
            api_key=api_key,
            cache=settings.get("cache", True),
            cache_in_memory=settings.get("cache_in_memory", True),
            temperature=settings.get("temperature", 0.0),
            max_tokens=settings.get("max_tokens", 1000)
        )
        dspy.configure(lm=lm)
        print(f"DSPy configuration successful:")
        print(f"  - Model: {model_name}")
        print(f"  - Temperature: {settings.get('temperature', 0.0)}")
        print(f"  - Caching: {'enabled' if settings.get('cache', True) else 'disabled'}")
        return True
    except Exception as e:
        print(f"Error configuring DSPy: {e}")
        print(traceback.format_exc())
        return False


def create_dynamic_signature(entity_type: str, entity_description: str, dimensions: List[Dict], output_fields: List[Dict] = None):
    """Create a dynamically constructed Signature class based on dimensions.
    
    Args:
        entity_type: The type of entity
        entity_description: Description of the entity type
        dimensions: List of dimension dictionaries defining input attributes
        output_fields: List of output field dictionaries (optional)
        
    Returns:
        A new DSPy Signature class with appropriate input/output fields
    """
    # Create a new Signature class dynamically using type()
    attributes = {
        "__doc__": f"""
        Generate a cohesive and believable entity based on the provided attributes.
        
        Entity Type: {entity_type}
        Description: {entity_description}
        """,
        
        # Standard input fields
        "entity_type": dspy.InputField(desc=f"The entity type: {entity_type}"),
        "entity_description": dspy.InputField(desc=f"Description of the entity type: {entity_description}"),
        "variability": dspy.InputField(desc="The level of creativity to use (0=typical, 0.5=distinct, 1=unique)"),
        
        # Standard output fields - always present
        "name": dspy.OutputField(desc="A name for this entity, based on the entity data provided"),
        "backstory": dspy.OutputField(desc="A cohesive description of the entity that incorporates all the provided attributes")
    }
    
    # Add dynamic input fields based on dimensions
    for dim in dimensions:
        field_name = f"dim_{dim['name']}"
        field_desc = dim.get('description', f"The {dim['name']} of this entity")
        
        # Add specific context based on dimension type
        if dim['type'] == 'categorical' and 'options' in dim:
            options_str = ", ".join(dim['options'])
            field_desc += f" (one of: {options_str})"
        elif dim['type'] == 'numerical' and 'min_value' in dim and 'max_value' in dim:
            field_desc += f" (between {dim['min_value']} and {dim['max_value']})"
        elif dim['type'] == 'boolean':
            field_desc += " (true or false)"
            
        # Add to attributes dictionary
        attributes[field_name] = dspy.InputField(desc=field_desc)
    
    # Add dynamic output fields if specified
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
    return type('DynamicEntitySignature', (dspy.Signature,), attributes)


def generate_dimension_values(dimensions: List[Dict]) -> Dict[str, Any]:
    """Generate random values for dimensions based on their types.
    
    Args:
        dimensions: List of dimension dictionaries
        
    Returns:
        Dictionary with randomly generated values for each dimension
    """
    values = {}
    
    for dim in dimensions:
        dim_type = dim.get('type', 'text')
        dim_name = dim.get('name', '')
        
        if dim_type == 'categorical':
            if not 'options' in dim:
                continue
                
            options = dim['options']
            distribution_values = dim.get('distribution_values', {})
            
            if distribution_values and all(option in distribution_values for option in options):
                # Use provided distribution
                weights = [distribution_values.get(option, 0) for option in options]
                # Normalize weights to ensure they sum to 1
                total = sum(weights)
                if total > 0:
                    normalized_weights = [w/total for w in weights]
                    values[dim_name] = random.choices(options, weights=normalized_weights, k=1)[0]
                else:
                    # Fallback to uniform if weights sum to 0
                    values[dim_name] = random.choice(options)
            else:
                # Uniform selection if no distribution values
                values[dim_name] = random.choice(options)
                
        elif dim_type in ['int', 'float']:
            min_val = dim.get('min_value', 0)
            max_val = dim.get('max_value', 100)
            distribution = dim.get('distribution', 'uniform')
            
            if distribution == 'uniform':
                # Uniform distribution between min and max
                if dim_type == 'int':
                    values[dim_name] = random.randint(int(min_val), int(max_val))
                else:
                    values[dim_name] = random.uniform(min_val, max_val)
                    
            elif distribution == 'normal':
                # Normal distribution with mean at center of range and specified std_deviation
                mean = (min_val + max_val) / 2
                
                # Use spread_factor if available (new approach) or fall back to std_deviation (legacy)
                if 'spread_factor' in dim:
                    # Convert spread factor to appropriate standard deviation based on range
                    spread_factor = dim.get('spread_factor', 0.5)  # 0=concentrated, 1=spread
                    std_dev = spread_factor * (max_val - min_val) / 6
                else:
                    # Legacy behavior: use specified std_deviation or default
                    std_dev = dim.get('std_deviation', (max_val - min_val) / 6)  # Default to range/6
                
                # Generate value and clip to min-max range
                value = random.normalvariate(mean, std_dev)
                value = max(min_val, min(max_val, value))
                
                if dim_type == 'int':
                    values[dim_name] = int(round(value))
                else:
                    values[dim_name] = value
                    
            elif distribution == 'skewed':
                # Skewed distribution using beta distribution with skew_factor
                skew_factor = dim.get('skew_factor', 0)  # -5 to 5, 0 is symmetric
                
                if skew_factor == 0:
                    # No skew, use uniform
                    if dim_type == 'int':
                        values[dim_name] = random.randint(int(min_val), int(max_val))
                    else:
                        values[dim_name] = random.uniform(min_val, max_val)
                else:
                    # Adjust alpha and beta parameters based on skew_factor
                    if skew_factor < 0:  # Left skew
                        alpha = 1 + abs(skew_factor)
                        beta = 1.0
                    else:  # Right skew
                        alpha = 1.0
                        beta = 1 + abs(skew_factor)
                    
                    # Generate value from beta distribution (0 to 1) and scale to range
                    beta_value = random.betavariate(alpha, beta)
                    scaled_value = min_val + beta_value * (max_val - min_val)
                    
                    if dim_type == 'int':
                        values[dim_name] = int(round(scaled_value))
                    else:
                        values[dim_name] = scaled_value
                
        elif dim_type == 'boolean':
            # Generate boolean based on true_percentage
            true_percentage = dim.get('true_percentage', 0.5)
            values[dim_name] = random.random() < true_percentage
            
        # Handle legacy 'numerical' type for backward compatibility    
        elif dim_type == 'numerical':
            min_val = dim.get('min_value', 0)
            max_val = dim.get('max_value', 100)
            if isinstance(min_val, int) and isinstance(max_val, int):
                values[dim_name] = random.randint(min_val, max_val)
            else:
                values[dim_name] = round(random.uniform(min_val, max_val), 2)
                
        elif dim_type == 'text':
            # Skip text dimensions - they'll be generated by LLM
            pass
    
    return values


# Create the module that uses dynamic signatures
class DynamicEntityCreator(dspy.Module):
    def __init__(self):
        super().__init__()
        # We'll create the predictor dynamically for each entity type
    
    def format_dimension_value(self, value):
        """Format a dimension value for display."""
        if isinstance(value, bool):
            return "Yes" if value else "No"
        return str(value)
    
    def forward(self, entity_type, entity_description, dimensions, variability=0.5, dimension_values=None, output_fields=None):
        """Generate a character with name and backstory using dynamic signature.
        
        Args:
            entity_type: The type of entity to create
            entity_description: Description of the entity
            dimensions: List of dimension definitions
            variability: Level of creativity (0=typical, 0.5=distinct, 1=unique)
            dimension_values: Dictionary of predefined dimension values (optional)
            output_fields: List of additional output fields to generate (optional)
        """
        # Generate random values for dimensions if not provided
        if dimension_values is None:
            dimension_values = generate_dimension_values(dimensions)
        
        # Print the dimensions and their values
        print("\nDimension values:")
        for dim in dimensions:
            if dim['name'] in dimension_values:
                print(f"  - {dim['name']}: {self.format_dimension_value(dimension_values[dim['name']])}")
        
        # Create a dynamic signature based on the entity type and dimensions
        DynamicSignature = create_dynamic_signature(entity_type, entity_description, dimensions, output_fields)
        
        # Create a predictor with this signature
        predictor = dspy.Predict(DynamicSignature)
        
        # Build input arguments for the prediction
        input_args = {
            "entity_type": entity_type,
            "entity_description": entity_description,
            "variability": variability
        }
        
        # Add each dimension value as a separate input argument
        for dim in dimensions:
            if dim['name'] in dimension_values:
                input_args[f"dim_{dim['name']}"] = dimension_values[dim['name']]
        
        # Debug info
        print("\nSending query with the following parameters:")
        for key, value in input_args.items():
            print(f"  - {key}: {value}")
        
        if output_fields:
            print("\nRequesting additional output fields:")
            for field in output_fields:
                print(f"  - {field.get('name')}: {field.get('description')}")
        
        # Make the prediction
        result = predictor(**input_args)
        
        # Debug the result
        print("\nReceived prediction result:")
        print(f"  Result type: {type(result).__name__}")
        print(f"  Available attributes: {dir(result)}")
        
        # Extract and return the output in the expected format
        # Create a structured result with the expected fields
        class EntityResult:
            def __init__(self, name, backstory, additional_fields=None):
                self.name = name
                self.backstory = backstory
                
                # Add any additional fields
                if additional_fields:
                    for field_name, field_value in additional_fields.items():
                        setattr(self, field_name, field_value)
        
        # Try to extract name and backstory from different possible result formats
        name = None
        backstory = None
        additional_fields = {}
        
        if hasattr(result, 'name'):
            name = result.name
        elif hasattr(result, 'output') and isinstance(result.output, dict) and 'name' in result.output:
            name = result.output['name']
        
        if hasattr(result, 'backstory'):
            backstory = result.backstory
        elif hasattr(result, 'output') and isinstance(result.output, dict) and 'backstory' in result.output:
            backstory = result.output['backstory']
        
        # Extract additional output fields if any
        if output_fields:
            for field in output_fields:
                field_name = field.get('name')
                if hasattr(result, field_name):
                    additional_fields[field_name] = getattr(result, field_name)
                elif hasattr(result, 'output') and isinstance(result.output, dict) and field_name in result.output:
                    additional_fields[field_name] = result.output[field_name]
        
        # Create a simple fallback if needed
        if name is None or backstory is None:
            # Try to parse from result text if possible
            if hasattr(result, 'output') and isinstance(result.output, str):
                # Try to extract name and backstory from the text
                text = result.output
                
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
            additional_fields=additional_fields
        )

    async def generate_entity_async(self, entity_type, entity_description, dimensions, variability=0.5, dimension_values=None, output_fields=None):
        """Async version of the entity generation function for parallel processing."""
        # This function mostly mirrors the forward method but is designed for async use
        if dimension_values is None:
            dimension_values = generate_dimension_values(dimensions)
        
        # Create a dynamic signature based on the entity type and dimensions
        DynamicSignature = create_dynamic_signature(entity_type, entity_description, dimensions, output_fields)
        
        # Create a predictor with this signature
        predictor = dspy.Predict(DynamicSignature)
        
        # Build input arguments for the prediction
        input_args = {
            "entity_type": entity_type,
            "entity_description": entity_description,
            "variability": variability
        }
        
        # Add each dimension value as a separate input argument
        for dim in dimensions:
            if dim['name'] in dimension_values:
                input_args[f"dim_{dim['name']}"] = dimension_values[dim['name']]
        
        # Use an event loop to run the synchronous predictor call
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            lambda: predictor(**input_args)
        )
        
        # Extract and return the output in the expected format
        # Create a structured result with the expected fields
        class EntityResult:
            def __init__(self, name, backstory, additional_fields=None, dimensions=None):
                self.name = name
                self.backstory = backstory
                self.dimension_values = dimensions or {}
                
                # Add any additional fields
                if additional_fields:
                    for field_name, field_value in additional_fields.items():
                        setattr(self, field_name, field_value)
        
        # Try to extract name and backstory from different possible result formats
        name = None
        backstory = None
        additional_fields = {}
        
        if hasattr(result, 'name'):
            name = result.name
        elif hasattr(result, 'output') and isinstance(result.output, dict) and 'name' in result.output:
            name = result.output['name']
        
        if hasattr(result, 'backstory'):
            backstory = result.backstory
        elif hasattr(result, 'output') and isinstance(result.output, dict) and 'backstory' in result.output:
            backstory = result.output['backstory']
        
        # Extract additional output fields if any
        if output_fields:
            for field in output_fields:
                field_name = field.get('name')
                if hasattr(result, field_name):
                    additional_fields[field_name] = getattr(result, field_name)
                elif hasattr(result, 'output') and isinstance(result.output, dict) and field_name in result.output:
                    additional_fields[field_name] = result.output[field_name]
        
        # Create a simple fallback if needed
        if name is None or backstory is None:
            # Try to parse from result text if possible
            if hasattr(result, 'output') and isinstance(result.output, str):
                # Try to extract name and backstory from the text
                text = result.output
                
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


def list_entities(entity_config):
    """List all available entity templates from config."""
    entities = entity_config.get("entity_inputs", [])
    if not entities:
        print("No entity templates found in config")
        return
    
    print("\nAvailable entity templates:")
    print("-" * 40)
    for i, entity in enumerate(entities, 1):
        dimensions = entity.get('dimensions', [])
        dim_count = len(dimensions)
        print(f"{i}. {entity.get('name', 'Unnamed')} - {entity.get('entity_type')} ({dim_count} dimensions)")
    print("-" * 40)


def get_entity_by_name(entity_config, entity_name):
    """Get entity configuration by name."""
    entities = entity_config.get("entity_inputs", [])
    for entity in entities:
        if entity.get("name") == entity_name:
            return entity
    return None


def get_entity_by_index(entity_config, index):
    """Get entity configuration by index (1-based)."""
    entities = entity_config.get("entity_inputs", [])
    if 1 <= index <= len(entities):
        return entities[index-1]
    return None


def get_default_entity(entity_config):
    """Get the default entity from config."""
    default_name = entity_config.get("default_entity")
    if default_name:
        entity = get_entity_by_name(entity_config, default_name)
        if entity:
            return entity
    
    # Fallback to first entity or create minimal default
    entities = entity_config.get("entity_inputs", [])
    if entities:
        return entities[0]
    
    return {
        "name": "Default Human",
        "entity_type": "Human",
        "entity_description": "A realistic human being",
        "variability": 0.5,
        "dimensions": []
    }


async def generate_entities_parallel(creator, entity_type, entity_description, dimensions, variability, output_fields, num_entities, max_parallel=50):
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
            
            # Print progress information
            print(f"\n--- Generating entity {i+1} of {num_entities} ---")
            print("\nDimension values:")
            for dim in dimensions:
                if dim['name'] in dimension_values:
                    value = dimension_values[dim['name']]
                    formatted_value = "Yes" if isinstance(value, bool) and value else "No" if isinstance(value, bool) else str(value)
                    print(f"  - {dim['name']}: {formatted_value}")
            
            # Debug info
            print("\nSending query with the following parameters:")
            input_args = {
                "entity_type": entity_type,
                "entity_description": entity_description,
                "variability": variability
            }
            for dim in dimensions:
                if dim['name'] in dimension_values:
                    input_args[f"dim_{dim['name']}"] = dimension_values[dim['name']]
                    
            for key, value in input_args.items():
                print(f"  - {key}: {value}")
            
            if output_fields:
                print("\nRequesting additional output fields:")
                for field in output_fields:
                    print(f"  - {field.get('name')}: {field.get('description')}")
            
            # Generate the entity
            try:
                entity = await creator.generate_entity_async(
                    entity_type, 
                    entity_description, 
                    dimensions, 
                    variability, 
                    dimension_values,
                    output_fields
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
    """Run entity generation with dynamic dimensions."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate an entity using DSPy with dynamic dimensions")
    parser.add_argument("--list", action="store_true", help="List available entity templates")
    parser.add_argument("--entity", type=str, help="Entity template name to use")
    parser.add_argument("--index", type=int, help="Entity template index to use (1-based)")
    parser.add_argument("--show-dimensions", action="store_true", help="Show dimensions for the selected entity")
    parser.add_argument("--count", "-n", type=int, help="Number of entities to generate")
    parser.add_argument("--max-parallel", "-p", type=int, default=50, help="Maximum number of parallel generation calls")
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
                elif dim_type == 'numerical' and 'min_value' in dim and 'max_value' in dim:
                    type_info = f"Range: {dim['min_value']} to {dim['max_value']}"
                
                print(f"{i}. {dim.get('name')}: {dim.get('description')} ({dim_type}) {type_info}")
        return
    
    # Configure DSPy
    if not setup_dspy(llm_config):
        sys.exit(1)
    
    # Determine how many entities to generate
    num_entities = args.count if args.count is not None else entity_config.get("num_entities", 1)
    max_parallel = min(args.max_parallel, 50)  # Limit to 50 max as requested
    
    # Create the dynamic module
    creator = DynamicEntityCreator()
    
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
    print(f"Using parallel processing with max {max_parallel} concurrent calls")
    
    if output_fields:
        print(f"Including {len(output_fields)} additional output fields")
    
    try:
        # Store all generated entities
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