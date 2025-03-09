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

# Import the batch entity creator - use absolute path to avoid import issues
from llm.batch_entity_creator import (
    BatchEntityCreator, 
    load_config, 
    setup_dspy, 
    MAX_PARALLEL_ENTITIES
)

# Import storage module for database operations
import storage

# Load environment variables
load_dotenv()

# Create a Blueprint for batch entity routes
batch_entity_bp = Blueprint('batch_entity', __name__)

# Initialize the batch entity creator - we'll do this once when the module loads
# rather than on each request
creator = None
create_error = None

def get_creator():
    """Get the batch entity creator, initializing it if needed."""
    global creator, create_error
    
    if creator is not None:
        return creator, None
    
    try:
        # Try with empty config (will use environment variables)
        print("Initializing DSPy with empty config...")
        if not setup_dspy({}):
            raise Exception("Failed to set up DSPy with default settings")
        
        # Create a new batch entity creator
        creator = BatchEntityCreator()
        print("Successfully initialized batch entity creator")
        return creator, None
    except Exception as e:
        error_msg = f"Error initializing batch entity creator: {str(e)}"
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
    
    This endpoint is optimized to create multiple entities that are more diverse from each other
    than when generated individually, helping avoid similar names and descriptions.
    """
    global creator, create_error
    
    # Check if creator is initialized
    if creator is None:
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
        
        print(f"Parsed fields: entity_type={entity_type}, dimensions={len(dimensions)}, output_fields={len(output_fields)}")
        
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
            # Run the async generator in the event loop
            entities = loop.run_until_complete(
                creator.generate_batch_async(
                    entity_type=entity_type,
                    entity_description=entity_description,
                    dimensions=dimensions,
                    variability=variability,
                    batch_size=batch_size,
                    output_fields=output_fields
                )
            )
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
    """
    Get the current configuration for batch entity generation
    
    Returns the maximum number of entities that can be generated in a batch
    and whether the creator has been initialized.
    """
    global creator, create_error
    
    # Get creator status
    is_initialized = creator is not None
    error = create_error if not is_initialized else None
    
    return jsonify({
        "max_parallel_entities": MAX_PARALLEL_ENTITIES,
        "initialized": is_initialized,
        "error": error,
        "version": "1.0.2"
    }), 200

@batch_entity_bp.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint for the batch entity API."""
    global creator, create_error
    
    return jsonify({
        "status": "online", 
        "creator_initialized": creator is not None,
        "initialization_error": create_error
    }), 200 