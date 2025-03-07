"""
Example of how to integrate the entity type dimensions generator with the API.

This file shows how to add an endpoint to generate dimensions for entity types.
"""

from flask import Flask, request, jsonify
import logging
import sys
import os
from pathlib import Path

# Add the project root directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import the entity type dimensions generator
from backend.llm.entity_type_generator import generate_entity_type_dimensions, LLMError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create a Flask app instance
app = Flask(__name__)


def success_response(data, status_code=200):
    """
    Create a success response.
    
    Args:
        data: The data to include in the response
        status_code: HTTP status code (default: 200)
        
    Returns:
        A JSON response with the data and status code
    """
    return jsonify(data), status_code


def error_response(message, status_code=400):
    """
    Create an error response.
    
    Args:
        message: Error message
        status_code: HTTP status code (default: 400)
        
    Returns:
        A JSON response with the error message and status code
    """
    return jsonify({"error": message}), status_code


@app.route('/api/entity-types/generate-dimensions', methods=['POST'])
def generate_entity_type_dimensions_endpoint():
    """
    Generate dimensions for an entity type based on name and description.
    
    Expected JSON payload:
    {
        "entity_type_name": "Fantasy Character",
        "entity_type_description": "A detailed fantasy character...",
        "n_dimensions": 8
    }
    
    Returns:
        A JSON response with the generated dimensions
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required fields
        if not data.get('entity_type_name'):
            return error_response("entity_type_name is required")
        
        if not data.get('entity_type_description'):
            return error_response("entity_type_description is required")
        
        # Get parameters from request
        entity_type_name = data.get('entity_type_name')
        entity_type_description = data.get('entity_type_description')
        n_dimensions = data.get('n_dimensions', 5)
        
        # Generate dimensions
        dimensions = generate_entity_type_dimensions(
            entity_type_name=entity_type_name,
            entity_type_description=entity_type_description,
            n_dimensions=n_dimensions
        )
        
        # Return success response with dimensions
        return success_response({
            "entity_type_name": entity_type_name,
            "entity_type_description": entity_type_description,
            "dimensions": dimensions
        })
        
    except LLMError as e:
        # Handle LLM-specific errors
        logger.error(f"LLM error: {str(e)}")
        return error_response(f"Error generating dimensions: {str(e)}", 500)
    
    except ValueError as e:
        # Handle validation errors
        logger.error(f"Validation error: {str(e)}")
        return error_response(str(e), 400)
    
    except Exception as e:
        # Handle other exceptions
        logger.error(f"Unexpected error: {str(e)}")
        return error_response("An unexpected error occurred", 500)


# Integration with existing create_entity_type endpoint
"""
# Add to your existing app.py or Flask application:

@app.route('/api/entity-types/suggest-dimensions', methods=['POST'])
@handle_exceptions
def suggest_entity_type_dimensions():
    # Get JSON data from request
    data = request.get_json()
    
    # Validate required fields
    if not data.get('name'):
        return error_response("name is required")
    
    if not data.get('description'):
        return error_response("description is required")
    
    # Get parameters from request
    entity_type_name = data.get('name')
    entity_type_description = data.get('description') 
    n_dimensions = data.get('n_dimensions', 5)
    
    try:
        # Generate dimensions
        dimensions = generate_entity_type_dimensions(
            entity_type_name=entity_type_name,
            entity_type_description=entity_type_description,
            n_dimensions=n_dimensions
        )
        
        # Return success response with dimensions
        return success_response({
            "name": entity_type_name,
            "description": entity_type_description,
            "dimensions": dimensions
        })
    except Exception as e:
        return error_response(f"Error generating dimensions: {str(e)}", 500)
"""


if __name__ == "__main__":
    app.run(debug=True, port=5000) 