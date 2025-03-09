"""
Batch Entity Creator - Generates multiple diverse entities in a single request

This module extends the functionality of simple_entity_creator.py by implementing
a batch generation approach that creates multiple diverse entities at once.
This helps avoid generating too similar entities with the same names and descriptions.
"""

import os
import json
import traceback
import asyncio
import random
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

import dspy

# Load environment variables
load_dotenv()

# Get MAX_PARALLEL_ENTITIES from environment or default to 10
MAX_PARALLEL_ENTITIES = int(os.getenv("MAX_PARALLEL_ENTITIES", "10"))

def load_config(config_path, config_type):
    """Load configuration from JSON file with error handling.
    
    Args:
        config_path: Path to the JSON config file
        config_type: Type of configuration for error messages
        
    Returns:
        Dictionary containing the config or empty dict on error
    """
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
    """Configure DSPy with settings from config or environment variables.
    
    Args:
        llm_config: Dictionary containing LLM configuration
        
    Returns:
        Boolean indicating whether setup was successful
    """
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

def generate_dimension_values(dimensions: List[Dict]) -> Dict[str, Any]:
    """Generate random values for each dimension based on its type.
    
    Args:
        dimensions: List of dimension dictionaries
        
    Returns:
        Dictionary mapping dimension names to randomly generated values
    """
    values = {}
    for dim in dimensions:
        name = dim['name']
        dim_type = dim['type']
        
        if dim_type == 'numeric':
            min_val = dim.get('min', 0)
            max_val = dim.get('max', 100)
            values[name] = random.uniform(min_val, max_val)
            
            # Round to specified precision if provided
            if 'precision' in dim:
                values[name] = round(values[name], dim['precision'])
            
        elif dim_type == 'categorical':
            if 'options' in dim:
                values[name] = random.choice(dim['options'])
            else:
                values[name] = f"Random {name}"
                
        elif dim_type == 'boolean':
            values[name] = random.choice([True, False])
            
        elif dim_type == 'text':
            # Just assign a placeholder for text fields
            values[name] = f"default {name}"
            
    return values

def create_batch_signature(entity_type: str, entity_description: str, dimensions: List[Dict], output_fields: List[Dict] = None, batch_size: int = MAX_PARALLEL_ENTITIES):
    """Create a dynamically constructed Signature class for batch entity generation.
    
    This function creates a proper class-based DSPy signature with type annotations
    for generating multiple diverse entities in a single request.
    
    Args:
        entity_type: The type of entity
        entity_description: Description of the entity type
        dimensions: List of dimension dictionaries defining input attributes
        output_fields: List of output field dictionaries (optional)
        batch_size: Number of entities to generate in a batch
        
    Returns:
        A new DSPy Signature class with appropriate input/output fields
    """
    # Define a dynamic DSPy signature class using type() 
    signature_doc = f"""
    Generate {batch_size} diverse and unique {entity_type} entities.
    
    Entity Type: {entity_type}
    Description: {entity_description}
    
    Each entity should be different from the others in meaningful ways.
    Avoid using similar names or descriptions across entities.
    Each entity should have a unique name that fits its attributes.
    """
    
    # Build the entities description
    entities_desc = f"""
    A list of exactly {batch_size} unique and diverse {entity_type} entities. 
    Each entity must be a JSON object with at minimum 'name' and 'backstory' fields.
    Make sure each entity has a different name and backstory from all others.
    Format as a valid JSON array of objects: [{{"name": "Entity1", "backstory": "..."}},...] 
    """
    
    # If there are additional output fields, include them in the description
    if output_fields:
        additional_fields_desc = ", ".join([f"'{field['name']}'" for field in output_fields])
        entities_desc = f"""
        A list of exactly {batch_size} unique and diverse {entity_type} entities. 
        Each entity must be a JSON object with 'name', 'backstory', and {additional_fields_desc} fields.
        Make sure each entity has a different name and backstory from all others.
        Format as a valid JSON array of objects: [{{"name": "Entity1", "backstory": "...", 
        {", ".join([f'"{field["name"]}": "..."' for field in output_fields])}}},...] 
        """
    
    # Create the class attributes with annotations in the format expected by type()
    class_body = {
        "__doc__": signature_doc,
        "entity_type": dspy.InputField(desc=f"The entity type: {entity_type}"),
        "entity_description": dspy.InputField(desc=f"Description of the entity type: {entity_description}"),
        "n_entities": dspy.InputField(desc=f"The number of entities to generate: {batch_size}"),
        "variability": dspy.InputField(desc="The level of creativity to use (0=typical, 0.5=distinct, 1=unusual)"),
        "dimensions_json": dspy.InputField(desc="JSON string containing dimension definitions and values for each entity"),
        "entities": dspy.OutputField(desc=entities_desc)
    }
    
    # Create and return the new class
    return type('BatchEntitySignature', (dspy.Signature,), class_body)

class BatchEntityCreator(dspy.Module):
    """DSPy module for creating batches of diverse entities."""
    
    def __init__(self):
        super().__init__()
    
    def format_dimension_value(self, value):
        """Format a dimension value for display.
        
        Args:
            value: The dimension value to format
            
        Returns:
            Formatted string representation of the value
        """
        if isinstance(value, bool):
            return "Yes" if value else "No"
        return str(value)
    
    def process_entities(self, result, batch_dimension_values, dimensions, output_fields=None):
        """Process the entities returned from the LLM.
        
        Args:
            result: The result object from the LLM prediction
            batch_dimension_values: The dimension values for each entity in the batch
            dimensions: The dimension definitions
            output_fields: Additional output fields definitions (optional)
            
        Returns:
            List of EntityResult objects
        """
        entities = []
        
        # Define EntityResult class for structured outputs
        class EntityResult:
            def __init__(self, name, backstory, additional_fields=None, dimensions=None):
                self.name = name
                self.backstory = backstory
                self.dimension_values = dimensions or {}
                
                # Add any additional fields
                if additional_fields:
                    for field_name, field_value in additional_fields.items():
                        setattr(self, field_name, field_value)
        
        # Check if we have entities in the result
        if not hasattr(result, 'entities'):
            print("No 'entities' attribute found in result")
            print(f"Available attributes: {dir(result)}")
            return entities
        
        # Get the entities from the result
        entity_list = result.entities
        
        # Debug information
        print(f"\nProcessing entities result: {type(entity_list)}")
        if isinstance(entity_list, str) and len(entity_list) > 0:
            print(f"First 200 chars: {entity_list[:200]}...")
        
        # If the result is a string, try to parse it as JSON
        if isinstance(entity_list, str):
            try:
                # Check if the string is wrapped in backticks or similar markers and remove them
                cleaned_str = entity_list.strip()
                if cleaned_str.startswith('```') and cleaned_str.endswith('```'):
                    cleaned_str = cleaned_str[3:-3].strip()
                if cleaned_str.startswith('```json') and cleaned_str.endswith('```'):
                    cleaned_str = cleaned_str[7:-3].strip()
                if cleaned_str.startswith('json') and cleaned_str.endswith('```'):
                    cleaned_str = cleaned_str[4:-3].strip()
                    
                entity_list = json.loads(cleaned_str)
                print(f"Successfully parsed entities JSON with {len(entity_list)} entities")
            except json.JSONDecodeError as e:
                print(f"Error parsing entities result as JSON: {e}")
                
                # Attempt to extract JSON from the string using a regex approach
                import re
                json_pattern = r'\[[\s\S]*\]'
                matches = re.search(json_pattern, entity_list)
                if matches:
                    try:
                        entity_list = json.loads(matches.group(0))
                        print(f"Successfully extracted and parsed JSON with regex: {len(entity_list)} entities")
                    except json.JSONDecodeError:
                        print("Failed to parse JSON with regex extraction")
                        entity_list = []
                else:
                    entity_list = []
        
        # Ensure entity_list is a list
        if not isinstance(entity_list, list):
            print(f"Entity result is not a list, type: {type(entity_list)}")
            if isinstance(entity_list, dict) and 'entities' in entity_list:
                entity_list = entity_list['entities']
            elif hasattr(entity_list, 'items') and callable(getattr(entity_list, 'items')):
                # If it's a dict-like object but not a dict
                entity_list = [entity_list]
            else:
                try:
                    # Try to convert to a list if possible
                    entity_list = list(entity_list)
                except:
                    entity_list = []
        
        # Process each entity in the batch
        for i, entity_data in enumerate(entity_list):
            # Get the index to map to the original dimension values
            entity_index = min(i, len(batch_dimension_values) - 1)
            dimension_values = batch_dimension_values[entity_index]
            
            # Handle different entity data formats
            if isinstance(entity_data, dict):
                # Dictionary format (expected)
                name = entity_data.get('name', f"Entity {i+1}")
                backstory = entity_data.get('backstory', f"No backstory provided for entity {i+1}")
                
                # Extract additional fields if present
                additional_fields = {}
                if output_fields:
                    for field in output_fields:
                        field_name = field.get('name')
                        if field_name in entity_data:
                            additional_fields[field_name] = entity_data[field_name]
                
                entity = EntityResult(name, backstory, additional_fields, dimension_values)
                entities.append(entity)
                print(f"Processed entity {i+1}: {name}")
            elif isinstance(entity_data, str):
                # Simple string format (fallback)
                name = f"Entity {i+1}"
                backstory = entity_data
                entity = EntityResult(name, backstory, {}, dimension_values)
                entities.append(entity)
                print(f"Processed string entity {i+1}")
            else:
                print(f"Skipping entity {i+1}: Unknown format {type(entity_data)}")
        
        return entities
    
    def forward(self, entity_type, entity_description, dimensions, variability=0.5, batch_size=MAX_PARALLEL_ENTITIES, output_fields=None):
        """Generate multiple diverse entities with names and backstories.
        
        Args:
            entity_type: The type of entity to create
            entity_description: Description of the entity
            dimensions: List of dimension definitions
            variability: Level of creativity (0=typical, 0.5=distinct, 1=unique)
            batch_size: Number of entities to generate in a batch
            output_fields: List of additional output fields to generate (optional)
            
        Returns:
            List of EntityResult objects containing the generated entities
        """
        # Generate a list of dimension values for each entity in the batch
        batch_dimension_values = []
        for _ in range(batch_size):
            dimension_values = generate_dimension_values(dimensions)
            batch_dimension_values.append(dimension_values)
        
        # Print information about dimensions for the batch
        print(f"\nGenerating a batch of {batch_size} entities with dimensions:")
        for i, dim_values in enumerate(batch_dimension_values[:3]):  # Show first 3 as examples
            print(f"\nEntity {i+1} dimension values:")
            for dim in dimensions:
                if dim['name'] in dim_values:
                    print(f"  - {dim['name']}: {self.format_dimension_value(dim_values[dim['name']])}")
        
        if batch_size > 3:
            print(f"... and {batch_size - 3} more entities")
        
        # Create a dynamic signature for batch generation
        BatchSignature = create_batch_signature(
            entity_type, 
            entity_description, 
            dimensions, 
            output_fields,
            batch_size
        )
        
        # Create a predictor with this signature
        # Use ChainOfThought for better reasoning and structured outputs
        predictor = dspy.ChainOfThought(BatchSignature)
        
        # Serialize dimension values to JSON string for the batch
        # Include both dimension definitions and values in a structured format
        batch_data = []
        for entity_index, dim_values in enumerate(batch_dimension_values):
            entity_data = {
                "entity_index": entity_index,
                "dimensions": {}
            }
            
            for dim in dimensions:
                if dim['name'] in dim_values:
                    entity_data["dimensions"][dim['name']] = {
                        "value": dim_values[dim['name']],
                        "type": dim['type'],
                        "description": dim.get('description', f"The {dim['name']} of this entity")
                    }
                    
                    # Include options for categorical dimensions
                    if dim['type'] == 'categorical' and 'options' in dim:
                        entity_data["dimensions"][dim['name']]["options"] = dim['options']
                        
                    # Include min/max for numeric dimensions
                    if dim['type'] == 'numeric':
                        entity_data["dimensions"][dim['name']]["min"] = dim.get('min', 0)
                        entity_data["dimensions"][dim['name']]["max"] = dim.get('max', 100)
            
            batch_data.append(entity_data)
        
        dimensions_json = json.dumps(batch_data, indent=2)
        
        # Build input arguments for the prediction
        input_args = {
            "entity_type": entity_type,
            "entity_description": entity_description,
            "n_entities": batch_size,
            "variability": variability,
            "dimensions_json": dimensions_json
        }
        
        # Make the prediction
        try:
            result = predictor(**input_args)
            
            # Print reasoning if available (helpful for debugging)
            if hasattr(result, 'reasoning') and result.reasoning:
                print("\nLLM Reasoning:")
                print(result.reasoning[:500] + "..." if len(result.reasoning) > 500 else result.reasoning)
            
            # Process the entities
            return self.process_entities(result, batch_dimension_values, dimensions, output_fields)
            
        except Exception as e:
            print(f"Error during prediction: {e}")
            import traceback
            print(traceback.format_exc())
            return []
    
    async def generate_batch_async(self, entity_type, entity_description, dimensions, variability=0.5, batch_size=MAX_PARALLEL_ENTITIES, output_fields=None):
        """Async version of the batch entity generation function.
        
        Args:
            entity_type: The type of entity to create
            entity_description: Description of the entity
            dimensions: List of dimension definitions
            variability: Level of creativity (0=typical, 0.5=distinct, 1=unique)
            batch_size: Number of entities to generate in a batch
            output_fields: List of additional output fields to generate (optional)
            
        Returns:
            List of EntityResult objects containing the generated entities
        """
        # Generate dimension values for the batch
        batch_dimension_values = []
        for _ in range(batch_size):
            dimension_values = generate_dimension_values(dimensions)
            batch_dimension_values.append(dimension_values)
            
        # Create batch signature
        BatchSignature = create_batch_signature(
            entity_type, 
            entity_description, 
            dimensions, 
            output_fields,
            batch_size
        )
        
        # Create a predictor with this signature
        predictor = dspy.ChainOfThought(BatchSignature)
        
        # Serialize dimension values to JSON string for the batch
        batch_data = []
        for entity_index, dim_values in enumerate(batch_dimension_values):
            entity_data = {
                "entity_index": entity_index,
                "dimensions": {}
            }
            
            for dim in dimensions:
                if dim['name'] in dim_values:
                    entity_data["dimensions"][dim['name']] = {
                        "value": dim_values[dim['name']],
                        "type": dim['type'],
                        "description": dim.get('description', f"The {dim['name']} of this entity")
                    }
                    
                    # Include options for categorical dimensions
                    if dim['type'] == 'categorical' and 'options' in dim:
                        entity_data["dimensions"][dim['name']]["options"] = dim['options']
                        
                    # Include min/max for numeric dimensions
                    if dim['type'] == 'numeric':
                        entity_data["dimensions"][dim['name']]["min"] = dim.get('min', 0)
                        entity_data["dimensions"][dim['name']]["max"] = dim.get('max', 100)
            
            batch_data.append(entity_data)
        
        dimensions_json = json.dumps(batch_data, indent=2)
        
        # Build input arguments for the prediction
        input_args = {
            "entity_type": entity_type,
            "entity_description": entity_description,
            "n_entities": batch_size,
            "variability": variability,
            "dimensions_json": dimensions_json
        }
        
        # Run the synchronous predictor in an executor to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None, 
                lambda: predictor(**input_args)
            )
            
            # Process the entities
            return self.process_entities(result, batch_dimension_values, dimensions, output_fields)
        except Exception as e:
            print(f"Error during async prediction: {e}")
            import traceback
            print(traceback.format_exc())
            return []

def main():
    """Main function for testing batch entity creation."""
    # Load configuration
    llm_config = load_config("config/llm_config.json", "LLM")
    entity_config = load_config("config/entities/characters.json", "entity")
    
    # Set up DSPy
    if not setup_dspy(llm_config):
        print("Failed to set up DSPy. Exiting.")
        return
    
    # Get entity configuration
    if not entity_config:
        print("No entity configuration found. Creating a test configuration.")
        entity_config = {
            "type": "character",
            "description": "A fictional character for a story",
            "dimensions": [
                {
                    "name": "age",
                    "type": "numeric",
                    "min": 18,
                    "max": 80,
                    "description": "Age of the character in years"
                },
                {
                    "name": "profession",
                    "type": "categorical",
                    "options": ["Doctor", "Engineer", "Artist", "Teacher", "Athlete"],
                    "description": "The character's profession or main occupation"
                },
                {
                    "name": "personality",
                    "type": "categorical",
                    "options": ["Introverted", "Extroverted", "Analytical", "Creative", "Cautious"],
                    "description": "The character's dominant personality trait"
                }
            ],
            "output_fields": [
                {
                    "name": "appearance",
                    "description": "Physical description of the character"
                },
                {
                    "name": "motivation",
                    "description": "What drives or motivates this character"
                }
            ]
        }
    
    # Extract entity details
    entity_type = entity_config.get("type", "character")
    entity_description = entity_config.get("description", "A fictional character")
    dimensions = entity_config.get("dimensions", [])
    output_fields = entity_config.get("output_fields", [])
    
    # Create a batch entity creator
    creator = BatchEntityCreator()
    
    # Generate a batch of entities
    batch_size = int(os.getenv("MAX_PARALLEL_ENTITIES", "3"))  # Use a smaller number for testing
    print(f"Generating a batch of {batch_size} {entity_type} entities...")
    
    entities = creator.forward(
        entity_type=entity_type,
        entity_description=entity_description,
        dimensions=dimensions,
        variability=0.7,  # Use higher variability for more diverse results
        batch_size=batch_size,
        output_fields=output_fields
    )
    
    # Print the generated entities
    print(f"\nGenerated {len(entities)} entities:")
    for i, entity in enumerate(entities):
        print(f"\n--- Entity {i+1}: {entity.name} ---")
        print(f"Backstory: {entity.backstory}")
        
        # Print additional fields if any
        for field in output_fields:
            field_name = field.get("name")
            if hasattr(entity, field_name):
                print(f"{field_name.capitalize()}: {getattr(entity, field_name)}")
        
        # Print dimension values
        print("\nDimension values:")
        for dim in dimensions:
            if dim['name'] in entity.dimension_values:
                value = entity.dimension_values[dim['name']]
                formatted_value = "Yes" if isinstance(value, bool) and value else "No" if isinstance(value, bool) else str(value)
                print(f"  - {dim['name']}: {formatted_value}")

if __name__ == "__main__":
    main() 