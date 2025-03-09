"""
API routes for batch entity creation

This module provides Flask API endpoints for generating batches of diverse entities
in a single API call, addressing the issue of similar entities being generated.
"""

import os
import json
import asyncio
from typing import Dict, List, Any

from flask import Blueprint, request, jsonify
from dotenv import load_dotenv

# Import the batch entity creator
from llm.batch_entity_creator import (
    BatchEntityCreator, 
    load_config, 
    setup_dspy, 
    MAX_PARALLEL_ENTITIES
)

# Load environment variables
load_dotenv()

# Create a Blueprint for batch entity routes
batch_entity_bp = Blueprint('batch_entity', __name__)

# Initialize the batch entity creator
creator = None

def initialize_creator():
    """Initialize the batch entity creator with DSPy setup"""
    global creator
    
    if creator is not None:
        return True
    
    # Load LLM configuration
    llm_config = load_config("config/llm_config.json", "LLM")
    
    # Set up DSPy
    if not setup_dspy(llm_config):
        return False
    
    # Create a new batch entity creator
    creator = BatchEntityCreator()
    return True

@batch_entity_bp.route('/generate', methods=['POST'])
async def generate_batch():
    """
    Generate a batch of diverse, unique entities in a single request.
    
    This endpoint is optimized to create multiple entities that are more diverse from each other
    than when generated individually, helping avoid similar names and descriptions.
    
    Request JSON format:
    {
        "entity_type": "character",
        "entity_description": "A fictional character for a story",
        "dimensions": [
            {
                "name": "age",
                "type": "numeric",
                "min": 18,
                "max": 80,
                "description": "Age in years"
            },
            ...
        ],
        "output_fields": [
            {
                "name": "appearance",
                "description": "Physical description"
            },
            ...
        ],
        "variability": 0.7,
        "batch_size": 5
    }
    
    Response:
    {
        "status": "success",
        "requested_batch_size": 5,
        "actual_batch_size": 5,
        "entity_type": "character",
        "entities": [
            {
                "id": "character_1",
                "name": "Alice Smith",
                "backstory": "...",
                "dimensions": {"age": 25, ...},
                "appearance": "..."
            },
            ...
        ]
    }
    """
    # Initialize creator if not already initialized
    if not initialize_creator():
        return jsonify({
            "status": "error",
            "message": "Failed to initialize entity creator"
        }), 500
    
    try:
        # Parse request JSON
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        # Extract required fields
        entity_type = data.get("entity_type")
        entity_description = data.get("entity_description")
        dimensions = data.get("dimensions", [])
        output_fields = data.get("output_fields", [])
        
        # Use a higher default variability to encourage more diverse entities
        variability = float(data.get("variability", 0.7))
        
        # Get batch size with default and maximum limits
        requested_batch_size = int(data.get("batch_size", MAX_PARALLEL_ENTITIES))
        batch_size = min(requested_batch_size, MAX_PARALLEL_ENTITIES)
        
        # Validate required fields
        if not entity_type:
            return jsonify({
                "status": "error",
                "message": "entity_type is required"
            }), 400
            
        if not entity_description:
            return jsonify({
                "status": "error",
                "message": "entity_description is required"
            }), 400
            
        if not dimensions:
            return jsonify({
                "status": "error",
                "message": "dimensions array is required"
            }), 400
        
        # Generate entities asynchronously
        entities = await creator.generate_batch_async(
            entity_type=entity_type,
            entity_description=entity_description,
            dimensions=dimensions,
            variability=variability,
            batch_size=batch_size,
            output_fields=output_fields
        )
        
        # Format the response
        response_entities = []
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
            
            response_entities.append(entity_data)
        
        # Return successful response
        return jsonify({
            "status": "success",
            "requested_batch_size": requested_batch_size,
            "actual_batch_size": batch_size,
            "entity_type": entity_type,
            "entities": response_entities,
            "diversity_optimized": True
        }), 200
        
    except Exception as e:
        # Log the error
        import traceback
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
    return jsonify({
        "max_parallel_entities": MAX_PARALLEL_ENTITIES,
        "initialized": creator is not None,
        "version": "1.0.1"
    }), 200 