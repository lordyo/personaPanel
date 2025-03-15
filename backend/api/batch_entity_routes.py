"""
API routes for batch entity creation

This module provides Flask API endpoints for generating batches of diverse entities
in a single API call, addressing the issue of similar entities being generated.
"""

import os
import json
import asyncio
import traceback
from typing import Dict, List, Any

from flask import Blueprint, request, jsonify, current_app
from dotenv import load_dotenv

# Add the backend directory to the Python path for proper imports
import sys
import os.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Import the multi-step entity creator for improved diversity
from llm.multi_step_entity_creator import (
    MultiStepEntityCreator, 
    load_config, 
    setup_dspy, 
    generate_entities_parallel,
    get_random_bisociative_words
)

# As a fallback, also import the batch entity creator
from llm.batch_entity_creator import (
    BatchEntityCreator, 
    MAX_PARALLEL_ENTITIES
)

# Import storage module for database operations
import storage

# Load environment variables
load_dotenv()

# Create a Blueprint for batch entity routes
batch_entity_bp = Blueprint('batch_entity', __name__)

# Initialize the multi-step entity creator - we'll do this once when the module loads
# rather than on each request
creator = None
batch_creator = None  # Fallback creator
create_error = None

def get_creator():
    """Get the multi-step entity creator, initializing it if needed."""
    global creator, batch_creator, create_error
    
    if creator is not None:
        return creator, None
    
    try:
        # Try with empty config (will use environment variables)
        print("Initializing DSPy with empty config...")
        if not setup_dspy({}):
            raise Exception("Failed to set up DSPy with default settings")
        
        # Create a new multi-step entity creator
        creator = MultiStepEntityCreator()
        print("Successfully initialized multi-step entity creator")
        
        # Also initialize batch creator as fallback
        batch_creator = BatchEntityCreator()
        print("Successfully initialized batch entity creator (as fallback)")
        
        return creator, None
    except Exception as e:
        error_msg = f"Error initializing entity creator: {str(e)}"
        create_error = error_msg
        print(error_msg)
        print(traceback.format_exc())
        return None, error_msg

# Initialize the creator when the module loads
creator, create_error = get_creator()

@batch_entity_bp.route('/generate', methods=['POST'])
def generate_batch():
    """
    Generate a batch of diverse, unique entities in a single request.
    
    This endpoint uses the multi-step entity generation approach with
    bisociative fueling for higher inter-entity variance, producing entities
    with more diverse names, descriptions, and characteristics.
    """
    global creator, batch_creator, create_error
    
    # Check if creator is initialized
    if creator is None and batch_creator is None:
        if create_error:
            error_msg = create_error
        else:
            error_msg = "Entity creator not initialized and no error recorded"
        return jsonify({
            "status": "error",
            "message": error_msg
        }), 500
    
    try:
        # Parse request JSON
        try:
            data = request.get_json()
            print(f"Received request data: {json.dumps(data, indent=2)}")
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return jsonify({
                "status": "error",
                "message": f"Error parsing JSON: {str(e)}"
            }), 400
        
        if not data:
            print("No JSON data provided in request")
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        # Extract required fields
        entity_type = data.get("entity_type")
        entity_description = data.get("entity_description")
        dimensions = data.get("dimensions", [])
        output_fields = data.get("output_fields", [])
        
        # Check if the user explicitly requested a specific generation method
        # Default to multi-step if not specified
        generation_method = data.get("generation_method", "multi-step").lower()
        use_multi_step = generation_method != "batch"
        
        print(f"Parsed fields: entity_type={entity_type}, dimensions={len(dimensions)}, output_fields={len(output_fields)}")
        print(f"Using {'multi-step' if use_multi_step else 'batch'} generation method")
        
        # Use a higher default variability to encourage more diverse entities
        variability = float(data.get("variability", 0.7))
        
        # Get batch size with default and maximum limits
        requested_batch_size = int(data.get("batch_size", MAX_PARALLEL_ENTITIES))
        batch_size = min(requested_batch_size, MAX_PARALLEL_ENTITIES)
        
        # Validate required fields
        if not entity_type:
            print("Missing entity_type field")
            return jsonify({
                "status": "error",
                "message": "entity_type is required"
            }), 400
            
        if not entity_description:
            print("Missing entity_description field")
            return jsonify({
                "status": "error",
                "message": "entity_description is required"
            }), 400
            
        if not dimensions:
            print("Missing dimensions array")
            return jsonify({
                "status": "error",
                "message": "dimensions array is required"
            }), 400
        
        # Handle the async operation with a wrapper that makes it synchronous
        # Create a new event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run the appropriate generation method
            if use_multi_step and creator is not None:
                # Use multi-step entity generation with bisociative fueling
                print(f"Generating {batch_size} entities using multi-step approach with bisociative fueling")
                entities = loop.run_until_complete(
                    generate_entities_parallel(
                        creator=creator,
                        entity_type=entity_type,
                        entity_description=entity_description,
                        dimensions=dimensions,
                        variability=variability,
                        output_fields=output_fields,
                        num_entities=batch_size,
                        max_parallel=MAX_PARALLEL_ENTITIES
                    )
                )
                print(f"Successfully generated {len(entities)} entities using multi-step approach")
                print(f"Entity names: {', '.join([entity.name for entity in entities])}")
            else:
                # Fallback to batch generation if multi-step is not available
                # or explicitly requested
                print(f"Generating {batch_size} entities using batch approach (fallback)")
                entities = loop.run_until_complete(
                    batch_creator.generate_batch_async(
                        entity_type=entity_type,
                        entity_description=entity_description,
                        dimensions=dimensions,
                        variability=variability,
                        batch_size=batch_size,
                        output_fields=output_fields
                    )
                )
                print(f"Successfully generated {len(entities)} entities using batch approach")
                print(f"Entity names: {', '.join([entity.name for entity in entities])}")
        finally:
            # Close the loop when done
            loop.close()
        
        # Format the response
        response_entities = []
        entity_ids = []

        # Get the entity type from the database to ensure it exists
        entity_type_object = storage.get_entity_type(entity_type)
        if not entity_type_object:
            # Try to get it by name (if entity_type isn't already an ID)
            entity_types = storage.get_all_entity_types()
            entity_type_object = next((et for et in entity_types if et['name'] == entity_type), None)
            
            if not entity_type_object:
                return jsonify({
                    "status": "error",
                    "message": f"Entity type '{entity_type}' not found in database"
                }), 404
        
        entity_type_id = entity_type_object['id']
        
        for i, entity in enumerate(entities):
            # Create a unique ID for tracking in the response
            response_id = f"{entity_type}_{i+1}"
            
            # Extract entity data
            name = entity.name
            description = entity.backstory
            
            # Build attributes dictionary for storage
            attributes = {
                "backstory": entity.backstory
            }
            
            # Add dimension values
            for dim in dimensions:
                if dim["name"] in entity.dimension_values:
                    attributes[dim["name"]] = entity.dimension_values[dim["name"]]
            
            # Add additional fields
            for field in output_fields:
                field_name = field.get("name")
                if hasattr(entity, field_name):
                    attributes[field_name] = getattr(entity, field_name)
            
            # Save entity to database
            try:
                entity_id = storage.save_entity(entity_type_id, name, description, attributes)
                entity_ids.append(entity_id)
                print(f"Saved entity to database: {name} (ID: {entity_id})")
                
                # Build the response object with the actual database ID
                entity_data = {
                    "id": entity_id,
                    "name": name,
                    "description": description,
                    "attributes": attributes
                }
                
                response_entities.append(entity_data)
            except Exception as e:
                print(f"Error saving entity to database: {str(e)}")
                # Continue with next entity rather than failing entire batch
                continue
        
        # Return successful response
        return jsonify({
            "status": "success",
            "requested_batch_size": requested_batch_size,
            "actual_batch_size": batch_size,
            "entity_type": entity_type,
            "entity_type_id": entity_type_id,
            "entities": response_entities,
            "entity_ids": entity_ids,
            "generation_method": "multi-step" if use_multi_step else "batch",
            "diversity_optimized": True
        }), 200
        
    except Exception as e:
        # Log the error
        print(f"Error generating batch: {str(e)}")
        print(traceback.format_exc())
        
        # Return error response
        return jsonify({
            "status": "error",
            "message": f"Error generating entities: {str(e)}"
        }), 500

@batch_entity_bp.route('/config', methods=['GET'])
def get_config():
    """Get the configuration of the batch entity generator."""
    global creator, batch_creator, create_error
    
    status = "ok" if creator is not None or batch_creator is not None else "error"
    
    return jsonify({
        "status": status,
        "max_parallel_entities": MAX_PARALLEL_ENTITIES,
        "multi_step_enabled": creator is not None,
        "batch_enabled": batch_creator is not None,
        "error": create_error if create_error else None,
        "default_method": "multi-step",
        "generation_methods": ["multi-step", "batch"]
    }), 200 if status == "ok" else 500

@batch_entity_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    global creator, batch_creator, create_error
    
    status = "ok" if creator is not None or batch_creator is not None else "error"
    
    return jsonify({
        "status": status,
        "message": "Entity batch service is ready" if status == "ok" else create_error
    }), 200 if status == "ok" else 500 