"""
Main Flask application for the Entity Simulation Framework.

This module initializes the Flask application, configures it, and defines
the routes for the API endpoints.
"""

import os
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import dspy
import traceback
import logging
from functools import wraps
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
import json
import datetime
import sqlite3
import re
import copy

# Load environment variables from .env file
load_dotenv()

# Import modules
from core.entity import EntityType, EntityInstance, Dimension
from core.simulation import SimulationEngine, Context, InteractionType
from llm.dspy_modules import EntityGenerator
import storage as storage
from core.templates import get_template_names, get_template
from llm.interaction_module import InteractionSimulator, LLMError
from llm.entity_type_generator import generate_entity_type_dimensions

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Configure app logger
logger = logging.getLogger(__name__)

# Add file handler for general logs
general_handler = RotatingFileHandler(
    'logs/app.log', 
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
general_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(general_handler)

# Add specific handler for API calls
api_handler = RotatingFileHandler(
    'logs/api_calls.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
api_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))
api_logger = logging.getLogger('api')
api_logger.addHandler(api_handler)

# Add specific handler for entity generation
entity_handler = RotatingFileHandler(
    'logs/entity_generation.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
entity_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))
entity_logger = logging.getLogger('entity')
entity_logger.addHandler(entity_handler)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS to allow cross-origin requests from the frontend
CORS(app, supports_credentials=True)

# Initialize database
@app.before_first_request
def initialize():
    """Initialize the database before handling the first request."""
    storage.init_db()
    logger.info("Database initialized")

# Initialize LLM
lm = None
try:
    # Use the OpenAI API key from environment variables
    api_key = os.environ.get('OPENAI_API_KEY')
    model_name = os.environ.get('DSPY_MODEL', 'gpt-4o-mini')
    
    if api_key:
        # Use the current DSPy API for model initialization
        model_path = f"openai/{model_name}"
        lm = dspy.LM(model_path, api_key=api_key)
        dspy.configure(lm=lm)
        logger.info(f"DSPy configured with OpenAI model: {model_name}")
    else:
        logger.warning("No OPENAI_API_KEY found in environment variables.")
except Exception as e:
    logger.error(f"Failed to initialize LLM: {e}")
    logger.exception("Detailed initialization error:")

# Define response helper functions
def success_response(data, status_code=200):
    """
    Create a standard success response.
    
    Args:
        data: The data to return
        status_code: HTTP status code (default: 200)
        
    Returns:
        Flask response object
    """
    return make_response(jsonify({
        "status": "success",
        "data": data
    }), status_code)

def error_response(message, status_code=400):
    """
    Create a standard error response.
    
    Args:
        message: Error message
        status_code: HTTP status code (default: 400)
        
    Returns:
        Flask response object
    """
    return make_response(jsonify({
        "status": "error",
        "message": message
    }), status_code)

def handle_exceptions(f):
    """
    Decorator to handle exceptions in routes.
    
    Args:
        f: The route handler function
        
    Returns:
        Wrapped function that handles exceptions
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            # Log the API call
            api_logger = logging.getLogger('api')
            api_logger.info(f"API call: {request.method} {request.path}")
            
            # Only check for request.json on methods that typically have a request body
            if request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and request.is_json:
                api_logger.debug(f"Request data: {json.dumps(request.json)}")
                
            return f(*args, **kwargs)
        except LLMError as e:
            logger.error(f"LLM Error: {e}")
            api_logger.error(f"LLM Error in {request.path}: {e}")
            return error_response(f"LLM error: {str(e)}", 500)
        except ValueError as e:
            logger.error(f"Validation Error: {e}")
            api_logger.error(f"Validation Error in {request.path}: {e}")
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.error(traceback.format_exc())
            api_logger.error(f"Unexpected error in {request.path}: {e}")
            return error_response(f"Server error: {str(e)}", 500)
    return wrapped

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify API server is running.
    
    Returns:
        JSON response with status "ok" and API version information
    """
    return success_response({
        "status": "ok",
        "version": "1.0.0",
        "llm_configured": lm is not None
    })

@app.route('/api/entity-types', methods=['GET'])
@handle_exceptions
def get_entity_types():
    """
    Get all entity types.
    
    Returns:
        JSON response with list of all entity types
    """
    entity_types = storage.get_all_entity_types()
    return success_response(entity_types)

@app.route('/api/entity-types', methods=['POST'])
@handle_exceptions
def create_entity_type():
    """
    Create a new entity type.
    
    Request body:
        name: Name of the entity type
        description: Description of the entity type
        dimensions: List of dimension objects
        
    Returns:
        JSON response with the created entity type ID
    """
    data = request.json
    
    # Validate required fields
    if not data or not data.get('name') or not data.get('dimensions'):
        return error_response("Name and dimensions are required")
    
    name = data['name']
    description = data.get('description', '')
    dimensions = data['dimensions']
    
    # Validate dimensions
    if not isinstance(dimensions, list):
        return error_response("Dimensions must be a list")
    
    for dim in dimensions:
        if not dim.get('name') or not dim.get('type'):
            return error_response("Each dimension must have a name and type")
        
        dim_type = dim.get('type')
        
        # Validate categorical dimensions
        if dim_type == 'categorical' and (not dim.get('options') or not isinstance(dim.get('options'), list)):
            return error_response(f"Dimension '{dim.get('name')}' must have options as a list")
            
        # Validate numerical, int, and float dimensions
        if dim_type in ['numerical', 'int', 'float']:
            if 'min_value' not in dim or 'max_value' not in dim:
                return error_response(f"Dimension '{dim.get('name')}' must have min_value and max_value")
                
            if dim.get('min_value') >= dim.get('max_value'):
                return error_response(f"Dimension '{dim.get('name')}' min_value must be less than max_value")
                
            # Validate distribution parameters
            if dim.get('distribution') == 'normal':
                # Check spread_factor (new approach)
                if dim.get('spread_factor') is not None:
                    if dim.get('spread_factor') <= 0 or dim.get('spread_factor') > 1:
                        return error_response(f"Dimension '{dim.get('name')}' spread_factor must be between 0 and 1")
                # Check std_deviation (legacy approach)
                elif dim.get('std_deviation') is not None:
                    if dim.get('std_deviation') <= 0:
                        return error_response(f"Dimension '{dim.get('name')}' std_deviation must be positive")
    
    # Normalize categorical distribution values if needed
    for dim in dimensions:
        if dim.get('type') == 'categorical' and dim.get('distribution_values'):
            options = dim.get('options', [])
            distribution_values = dim.get('distribution_values', {})
            
            # Remove any distribution values for options that don't exist
            keys_to_remove = [key for key in distribution_values if key not in options]
            for key in keys_to_remove:
                distribution_values.pop(key, None)
                
            # Add missing options with 0 value
            for option in options:
                if option not in distribution_values:
                    distribution_values[option] = 0
                    
            # Normalize values to sum to 1
            total = sum(distribution_values.values())
            if total > 0:  # Avoid division by zero
                for key in distribution_values:
                    distribution_values[key] /= total
    
    entity_type_id = storage.save_entity_type(name, description, dimensions)
    logger.info(f"Created entity type: {name} (ID: {entity_type_id})")
    
    return success_response({"id": entity_type_id}, 201)

@app.route('/api/entity-types/<entity_type_id>', methods=['GET'])
@handle_exceptions
def get_entity_type(entity_type_id):
    """
    Get an entity type by ID.
    
    Args:
        entity_type_id: ID of the entity type
        
    Returns:
        JSON response with the entity type details
    """
    entity_type = storage.get_entity_type(entity_type_id)
    if not entity_type:
        return error_response(f"Entity type with ID {entity_type_id} not found", 404)
    
    return success_response(entity_type)

@app.route('/api/entity-types/<entity_type_id>', methods=['PUT'])
@handle_exceptions
def update_entity_type(entity_type_id):
    """
    Update an entity type by ID.
    
    Args:
        entity_type_id: ID of the entity type
    
    Request body:
        name: Name of the entity type
        description: Description of the entity type
        dimensions: List of dimension objects
        
    Returns:
        JSON response with the updated entity type
    """
    data = request.json
    
    # Check if entity type exists
    entity_type = storage.get_entity_type(entity_type_id)
    if not entity_type:
        return error_response(f"Entity type with ID {entity_type_id} not found", 404)
    
    # Validate required fields
    if not data or not data.get('name') or not data.get('dimensions'):
        return error_response("Name and dimensions are required")
    
    name = data['name']
    description = data.get('description', '')
    dimensions = data['dimensions']
    
    # Validate dimensions
    if not isinstance(dimensions, list):
        return error_response("Dimensions must be a list")
    
    for dim in dimensions:
        if not dim.get('name') or not dim.get('type'):
            return error_response("Each dimension must have a name and type")
            
        dim_type = dim.get('type')
        
        # Validate categorical dimensions
        if dim_type == 'categorical' and (not dim.get('options') or not isinstance(dim.get('options'), list)):
            return error_response(f"Dimension '{dim.get('name')}' must have options as a list")
            
        # Validate numerical, int, and float dimensions
        if dim_type in ['numerical', 'int', 'float']:
            if 'min_value' not in dim or 'max_value' not in dim:
                return error_response(f"Dimension '{dim.get('name')}' must have min_value and max_value")
                
            if dim.get('min_value') >= dim.get('max_value'):
                return error_response(f"Dimension '{dim.get('name')}' min_value must be less than max_value")
                
            # Validate distribution parameters
            if dim.get('distribution') == 'normal':
                # Check spread_factor (new approach)
                if dim.get('spread_factor') is not None:
                    if dim.get('spread_factor') <= 0 or dim.get('spread_factor') > 1:
                        return error_response(f"Dimension '{dim.get('name')}' spread_factor must be between 0 and 1")
                # Check std_deviation (legacy approach)
                elif dim.get('std_deviation') is not None:
                    if dim.get('std_deviation') <= 0:
                        return error_response(f"Dimension '{dim.get('name')}' std_deviation must be positive")
    
    # Normalize categorical distribution values if needed
    for dim in dimensions:
        if dim.get('type') == 'categorical' and dim.get('distribution_values'):
            options = dim.get('options', [])
            distribution_values = dim.get('distribution_values', {})
            
            # Remove any distribution values for options that don't exist
            keys_to_remove = [key for key in distribution_values if key not in options]
            for key in keys_to_remove:
                distribution_values.pop(key, None)
                
            # Add missing options with 0 value
            for option in options:
                if option not in distribution_values:
                    distribution_values[option] = 0
                    
            # Normalize values to sum to 1
            total = sum(distribution_values.values())
            if total > 0:  # Avoid division by zero
                for key in distribution_values:
                    distribution_values[key] /= total
    
    # Update the entity type
    storage.update_entity_type(entity_type_id, name, description, dimensions)
    logger.info(f"Updated entity type: {name} (ID: {entity_type_id})")
    
    updated_entity_type = storage.get_entity_type(entity_type_id)
    return success_response(updated_entity_type)

@app.route('/api/entities', methods=['POST'])
@handle_exceptions
def create_entity():
    """
    Create a new entity instance or multiple instances.
    
    Request body:
        entity_type_id: ID of the entity type
        name: Name of the entity (when not generating)
        description: Description of the entity (optional)
        attributes: Dictionary of attribute values (when not generating)
        generate: Boolean indicating whether to generate attributes using LLM (default: False)
        count: Number of entities to generate (when generate is True, default: 1)
        variability: Float between 0-1 indicating generation variability (default: 0.5)
        
    Returns:
        JSON response with the created entity ID(s)
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('entity_type_id'):
        return error_response("Entity type ID is required", 400)
    
    entity_type_id = data['entity_type_id']
    entity_type = storage.get_entity_type(entity_type_id)
    if not entity_type:
        return error_response(f"Entity type {entity_type_id} not found", 404)
    
    # Check if we should generate the entity
    generate = data.get('generate', False)
    count = data.get('count', 1)
    
    # Validate count
    try:
        count = int(count)
        if count < 1 or count > 100:
            return error_response("Count must be between 1 and 100", 400)
    except (ValueError, TypeError):
        return error_response("Count must be a valid integer", 400)
    
    if generate:
        # Use EntityGenerator to create entities
        try:
            entity_ids = []
            
            # Validate variability
            variability_level = data.get('variability', 0.5)
            try:
                variability_level = float(variability_level)
                if variability_level < 0 or variability_level > 1:
                    return error_response("Variability must be between 0 and 1", 400)
            except (ValueError, TypeError):
                return error_response("Variability must be a valid number", 400)
            
            # Convert numeric variability to text variability level
            if variability_level < 0.33:
                variability = "low"
            elif variability_level < 0.67:
                variability = "medium"
            else:
                variability = "high"
            
            # Get entity type dimensions
            dimensions = entity_type['dimensions']
            
            # Get entity type description if provided
            entity_description = data.get('entity_description', entity_type.get('description', ''))
            
            # Process entities in parallel using ThreadPoolExecutor
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            # Create a list to store generation failures
            failures = []
            
            # Function to generate a single entity with better error handling
            def generate_single_entity():
                # Each call uses a fresh generator instance to avoid caching between entities
                gen = EntityGenerator()
                try:
                    generated = gen.forward(
                        entity_type['name'],
                        dimensions,
                        variability,
                        entity_description
                    )
                    
                    logger.debug(f"Generated entity attributes: {generated['attributes']}")
                    logger.debug(f"Generated entity name: {generated['name']}")
                    
                    # Log to entity generation logger
                    entity_logger = logging.getLogger('entity')
                    entity_logger.info(f"Generated entity: {generated['name']} for type {entity_type['name']}")
                    entity_logger.debug(f"Entity attributes: {generated['attributes']}")
                    
                    name = generated['name']
                    description = generated.get('description', '')
                    attributes = generated.get('attributes', {})
                    
                    # Save entity to database
                    entity_id = storage.save_entity(entity_type_id, name, description, attributes)
                    logger.info(f"Created generated entity: {name} (ID: {entity_id})")
                    entity_logger.info(f"Saved entity to database: {name} (ID: {entity_id})")
                    
                    return {
                        "id": entity_id,
                        "name": name,
                        "type": entity_type['name'],
                        "description": description,
                        "attributes": attributes,
                        "success": True
                    }
                except Exception as e:
                    logger.error(f"Error generating single entity: {str(e)}")
                    # Return a failure object instead of raising an exception
                    return {
                        "error": str(e),
                        "type": entity_type['name'],
                        "success": False
                    }
            
            # Use ThreadPoolExecutor for concurrent entity generation
            entity_results = []
            successful_entities = 0
            
            with ThreadPoolExecutor(max_workers=min(count, 10)) as executor:
                # Submit all generation tasks
                future_to_entity = {executor.submit(generate_single_entity): i for i in range(count)}
                
                # Process as they complete
                for future in as_completed(future_to_entity):
                    try:
                        entity_result = future.result()
                        
                        # Check if generation was successful
                        if entity_result.get("success", False):
                            entity_ids.append(entity_result["id"])
                            entity_results.append(entity_result)
                            successful_entities += 1
                        else:
                            # Record the failure
                            failures.append({
                                "index": future_to_entity[future],
                                "error": entity_result.get("error", "Unknown error")
                            })
                    except Exception as exc:
                        logger.error(f"Entity generation task failed: {exc}")
                        failures.append({
                            "index": future_to_entity[future],
                            "error": str(exc)
                        })
            
            # Log summary of generation
            logger.info(f"Entity generation completed: {successful_entities} successful, {len(failures)} failed")
            
            # Return both IDs and the complete entity data, including failure information
            response_data = {
                "ids": entity_ids,
                "entities": entity_results,
                "total_requested": count,
                "successful": successful_entities
            }
            
            # Include failures if any occurred
            if failures:
                response_data["failures"] = failures
                
                # If all generations failed, return a 500 error
                if successful_entities == 0:
                    return error_response(
                        f"All {count} entity generations failed. First error: {failures[0]['error']}", 
                        500
                    )
                    
                # If some generations failed but others succeeded, return a partial success
                return success_response(response_data, 207)  # 207 Multi-Status
            
            # All successful
            return success_response(response_data, 201)
            
        except Exception as e:
            logger.error(f"Error in batch entity generation: {str(e)}")
            return error_response(f"Failed to generate entities: {str(e)}", 500)
    else:
        # Use provided name and attributes (single entity only)
        name = data.get('name')
        description = data.get('description', '')
        # Ensure attributes is a dictionary
        attributes = data.get('attributes', {})
        if isinstance(attributes, str):
            try:
                attributes = json.loads(attributes)
            except:
                logger.warning(f"Failed to parse attributes as JSON: {attributes}")
                attributes = {}
        
        if not name:
            return error_response("Name is required when not generating", 400)
    
        entity_id = storage.save_entity(entity_type_id, name, description, attributes)
        logger.info(f"Created entity: {name} (ID: {entity_id})")
    
        return success_response({
            "id": entity_id,
            "name": name,
            "type": entity_type['name'],
            "description": description,
            "attributes": attributes
        }, 201)

@app.route('/api/entities/<entity_id>', methods=['GET'])
@handle_exceptions
def get_entity(entity_id):
    """
    Get an entity by ID.
    
    Args:
        entity_id: ID of the entity
        
    Returns:
        JSON response with the entity details
    """
    entity = storage.get_entity(entity_id)
    if not entity:
        return error_response(f"Entity with ID {entity_id} not found", 404)
    
    return success_response(entity)

@app.route('/api/entity-types/<entity_type_id>/entities', methods=['GET'])
@handle_exceptions
def get_entities_by_type(entity_type_id):
    """
    Get all entities of a specific type.
    
    Args:
        entity_type_id: ID of the entity type
        
    Returns:
        JSON response with list of entities of the specified type
    """
    entities = storage.get_entities_by_type(entity_type_id)
    return success_response(entities)

@app.route('/api/simulations', methods=['POST'])
@handle_exceptions
def create_simulation():
    """
    Create a new simulation.
    
    Request body:
        context: Context description
        interaction_type: Type of interaction (solo, dyadic, group)
        entity_ids: List of entity IDs to include in simulation
        metadata: Optional metadata
        n_rounds: Number of rounds to simulate (default: 1)
        last_round_number: Number of the last round (for continuations)
        previous_interaction: Previous interaction (for continuations)
        
    Returns:
        JSON response with the simulation ID and result
    """
    data = request.json
    
    # Validate required fields
    if not data or not data.get('context') or not data.get('interaction_type') or not data.get('entity_ids'):
        return error_response("Context, interaction type, and entity IDs are required")
    
    context_desc = data['context']
    interaction_type = data['interaction_type']
    entity_ids = data['entity_ids']
    metadata = data.get('metadata', {})
    n_rounds = data.get('n_rounds', 1)  # Default to 1 round if not specified
    last_round_number = data.get('last_round_number', 0)  # For continuations
    previous_interaction = data.get('previous_interaction', None)  # For continuations
    
    # Validate interaction type
    if interaction_type not in ['solo', 'dyadic', 'group']:
        return error_response("Interaction type must be 'solo', 'dyadic', or 'group'")
    
    # Validate entity IDs based on interaction type
    if interaction_type == 'solo' and len(entity_ids) != 1:
        return error_response("Solo interaction requires exactly 1 entity")
    elif interaction_type == 'dyadic' and len(entity_ids) != 2:
        return error_response("Dyadic interaction requires exactly 2 entities")
    elif interaction_type == 'group' and len(entity_ids) < 3:
        return error_response("Group interaction requires at least 3 entities")
    
    # Validate n_rounds is positive
    try:
        n_rounds = int(n_rounds)
        if n_rounds <= 0:
            return error_response("n_rounds must be a positive integer")
    except ValueError:
        return error_response("n_rounds must be a valid integer")
    
    # Check if LLM is configured
    if not lm:
        return error_response("LLM is not configured", 503)
    
    # Fetch entities
    entities = []
    for entity_id in entity_ids:
        entity = storage.get_entity(entity_id)
        if not entity:
            return error_response(f"Entity with ID {entity_id} not found", 404)
        entities.append(entity)
    
    # Create context
    context_id = storage.save_context(context_desc, metadata)
    
    # Use unified InteractionSimulator for all interaction types
    simulator = InteractionSimulator()
    prediction = simulator.forward(
        entities=entities,
        context=context_desc,
        n_turns=n_rounds,
        last_turn_number=last_round_number,
        previous_interaction=previous_interaction
    )
    
    # Extract the content from the prediction
    result = prediction.content
    
    # Save simulation result
    simulation_id = storage.save_simulation(
        context_id,
        interaction_type,
        entity_ids,
        result,
        metadata
    )
    
    logger.info(f"Created simulation: {simulation_id} ({interaction_type})")
    
    return success_response({
        "id": simulation_id,
        "context_id": context_id,
        "result": result
    }, 201)

@app.route('/api/simulations/<simulation_id>', methods=['GET'])
@handle_exceptions
def get_simulation(simulation_id):
    """
    Get a simulation by ID.
    
    Args:
        simulation_id: ID of the simulation
        
    Returns:
        JSON response with the simulation details
    """
    simulation = storage.get_simulation(simulation_id)
    if not simulation:
        return error_response(f"Simulation with ID {simulation_id} not found", 404)
    
    # Get detailed entity information
    entities = []
    for entity_id in simulation['entity_ids']:
        entity = storage.get_entity(entity_id)
        if entity:
            # Add entity type information
            entity_type = storage.get_entity_type(entity['entity_type_id'])
            if entity_type:
                entity['entity_type_name'] = entity_type['name']
            
            # Ensure entity description is included
            if 'description' not in entity or not entity['description']:
                entity['description'] = 'No description available'
                
            entities.append(entity)
    
    simulation['entities'] = entities
    
    # Get context information
    context = storage.get_context(simulation['context_id'])
    if context:
        simulation['context'] = context
        
        # Calculate simulation name (use first few words of context or generic name)
        if not simulation.get('name'):
            if context and context.get('description'):
                words = context.get('description', '').split()
                if len(words) > 5:
                    name = ' '.join(words[:5]) + '...'
                else:
                    name = context.get('description')
                simulation['name'] = name
            else:
                simulation['name'] = f"Simulation {simulation.get('id', '')[-6:]}"
    
    # Format timestamp if present
    if 'timestamp' in simulation:
        simulation['created_at'] = simulation['timestamp']
    
    return success_response(simulation)

@app.route('/api/simulations/<simulation_id>', methods=['DELETE'])
@handle_exceptions
def delete_simulation(simulation_id):
    """
    Delete a simulation by ID.
    
    Args:
        simulation_id: ID of the simulation to delete
        
    Returns:
        JSON response indicating success or error
    """
    result = storage.delete_simulation(simulation_id)
    if not result:
        return error_response(f"Simulation with ID {simulation_id} not found or could not be deleted", 404)
    
    return success_response({"message": f"Simulation {simulation_id} deleted successfully"})

@app.route('/api/simulations', methods=['GET'])
@handle_exceptions
def get_simulations():
    """
    Get all simulations, possibly filtered.
    
    Query parameters:
        entity_id: Filter by entity ID
        context_id: Filter by context ID
        interaction_type: Filter by interaction type
        
    Returns:
        JSON response with list of simulations
    """
    # TODO: Implement filtering
    simulations = storage.get_all_simulations()
    
    # Enhance simulation data with context descriptions and entity names
    enhanced_simulations = []
    for simulation in simulations:
        # Add context information
        context = storage.get_context(simulation['context_id'])
        if context:
            simulation['context'] = context.get('description', '')
        else:
            simulation['context'] = ''
        
        # Add basic entity information
        entities_data = []
        for entity_id in simulation.get('entity_ids', []):
            entity = storage.get_entity(entity_id)
            if entity:
                entities_data.append({
                    'id': entity.get('id'),
                    'name': entity.get('name', 'Unnamed Entity')
                })
        
        simulation['entities'] = entities_data
        
        # Calculate simulation name (use first few words of context or generic name)
        if not simulation.get('name'):
            if context and context.get('description'):
                words = context.get('description', '').split()
                if len(words) > 5:
                    name = ' '.join(words[:5]) + '...'
                else:
                    name = context.get('description')
                simulation['name'] = name
            else:
                simulation['name'] = f"Simulation {simulation.get('id', '')[-6:]}"
        
        # Format timestamp as ISO string for 'created_at'
        if simulation.get('timestamp'):
            simulation['created_at'] = simulation.get('timestamp')
        
        enhanced_simulations.append(simulation)
    
    return success_response(enhanced_simulations)

@app.route('/api/templates', methods=['GET'])
@handle_exceptions
def get_templates():
    """
    Get all predefined entity templates.
    
    Returns:
        JSON response with list of template names and descriptions
    """
    try:
        # get_template_names() already returns the formatted list we need
        templates = get_template_names()
        return success_response(templates)
    except Exception as e:
        logger.error(f"Error retrieving templates: {str(e)}")
        logger.exception("Template retrieval error:")
        return error_response("Failed to retrieve templates", 500)

@app.route('/api/templates/<template_id>', methods=['GET'])
@handle_exceptions
def get_template_details(template_id):
    """
    Get details of a specific template.
    
    Args:
        template_id: ID of the template
        
    Returns:
        JSON response with the template details
    """
    template = get_template(template_id)
    if not template:
        return error_response(f"Template '{template_id}' not found", 404)
    
    return success_response(template)

@app.route('/api/templates/<template_id>/create', methods=['POST'])
@handle_exceptions
def create_entity_type_from_template(template_id):
    """
    Create a new entity type from a template.
    
    Args:
        template_id: ID of the template
        
    Request body:
        name: Optional custom name (defaults to template name)
        description: Optional custom description (defaults to template description)
        
    Returns:
        JSON response with the created entity type ID
    """
    template = get_template(template_id)
    if not template:
        return error_response(f"Template '{template_id}' not found", 404)
    
    data = request.json or {}
    
    name = data.get('name', template.get('name', template_id))
    description = data.get('description', template.get('description', ''))
    
    # Use dimensions from the request if provided, otherwise use template dimensions
    if 'dimensions' in data and isinstance(data['dimensions'], list):
        logger.info(f"Using custom dimensions from request for template {template_id}")
        dimensions = data['dimensions']
        
        # Ensure dimensions are in the correct format
        for dimension in dimensions:
            # Convert camelCase to snake_case for backend compatibility
            if 'minValue' in dimension and 'min_value' not in dimension:
                dimension['min_value'] = dimension.pop('minValue')
            if 'maxValue' in dimension and 'max_value' not in dimension:
                dimension['max_value'] = dimension.pop('maxValue')
    else:
        logger.info(f"Using default dimensions from template {template_id}")
        dimensions = template.get('dimensions', [])
        
        # Convert Dimension objects to dictionaries if needed
        if dimensions and hasattr(dimensions[0], '__dict__'):
            dimensions = [d.__dict__ for d in dimensions]
    
    try:
        entity_type_id = storage.save_entity_type(name, description, dimensions)
        logger.info(f"Created entity type from template {template_id}: {name} (ID: {entity_type_id})")
        
        return success_response({"id": entity_type_id}, 201)
    except Exception as e:
        logger.error(f"Error creating entity type from template: {str(e)}\n{traceback.format_exc()}")
        return error_response(f"Error creating entity type: {str(e)}", 500)

@app.route('/api/entities/<entity_id>', methods=['DELETE'])
@handle_exceptions
def delete_entity(entity_id):
    """
    Delete an entity by ID.
    
    Args:
        entity_id: ID of the entity to delete
        
    Returns:
        JSON response indicating success or failure
    """
    result = storage.delete_entity(entity_id)
    
    if result:
        logger.info(f"Deleted entity with ID: {entity_id}")
        return success_response({"deleted": True})
    else:
        return error_response(f"Entity with ID {entity_id} not found or could not be deleted", 404)

@app.route('/api/entity-types/<entity_type_id>/entities', methods=['DELETE'])
@handle_exceptions
def delete_entities_by_type(entity_type_id):
    """
    Delete all entities of a specific entity type.
    
    Args:
        entity_type_id: ID of the entity type
        
    Returns:
        JSON response with the number of entities deleted
    """
    # Check if entity type exists
    entity_type = storage.get_entity_type(entity_type_id)
    if not entity_type:
        return error_response(f"Entity type with ID {entity_type_id} not found", 404)
    
    count = storage.delete_entities_by_type(entity_type_id)
    logger.info(f"Deleted {count} entities of type: {entity_type_id}")
    
    return success_response({"count": count})

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify the Flask app is running correctly."""
    return success_response({
        "message": "API is functioning correctly!",
        "time": datetime.datetime.now().isoformat()
    })

@app.route('/api/unified-simulations', methods=['POST'])
@handle_exceptions
def create_unified_simulation():
    """
    Create a new simulation using the unified simulation framework.
    
    This endpoint creates a simulation that works with any number of entities,
    from solo interactions to group discussions.
    
    Request body:
        context: Text description of the situation or environment
        entities: List of entity IDs to include in the simulation
        n_turns: Number of turns to generate in each round (default: 1)
        simulation_rounds: Number of sequential LLM calls to make (default: 1)
        metadata: Optional metadata for the simulation
        name: Optional name for the simulation
    
    Returns:
        JSON response with simulation details
    """
    data = request.json
    
    # Extract request data
    context_desc = data.get('context')
    entity_ids = data.get('entities', [])
    n_turns = int(data.get('n_turns', 1))
    simulation_rounds = int(data.get('simulation_rounds', 1))
    metadata = data.get('metadata', {})
    simulation_name = data.get('name')
    
    # Validate inputs
    if not context_desc:
        return error_response("Context is required")
    
    if not entity_ids:
        return error_response("At least one entity is required")
    
    # Create the context
    context_id = storage.save_context(context_desc)
    
    # Get the entities
    entities = []
    for entity_id in entity_ids:
        entity = storage.get_entity(entity_id)
        if not entity:
            return error_response(f"Entity with ID {entity_id} not found", 404)
        entities.append(entity)
    
    # Determine interaction type
    if len(entities) == 1:
        interaction_type = "solo"
    elif len(entities) == 2:
        interaction_type = "dyadic"
    else:
        interaction_type = "group"
    
    # Initialize the simulator
    simulator = InteractionSimulator()
    
    # Run the simulation
    result = simulator.forward(
        entities=entities,
        context=context_desc,
        n_turns=n_turns
    )
    
    content = result.content
    final_turn_number = result.final_turn_number
    
    # Run additional rounds if requested
    for round_num in range(1, simulation_rounds):
        # Pass the previous content and final turn number for continuation
        round_result = simulator.forward(
            entities=entities,
            context=context_desc,
            n_turns=n_turns,
            last_turn_number=final_turn_number,
            previous_interaction=content
        )
        
        # Append the new content
        content += f"\n\n{round_result.content}"
        final_turn_number = round_result.final_turn_number
    
    # Update metadata with rounds info
    metadata['simulation_rounds'] = simulation_rounds
    metadata['n_turns'] = n_turns
    metadata['total_turns'] = n_turns * simulation_rounds
    
    # If no name provided, create one with the entities
    if not simulation_name:
        entity_names = [entity.get('name', 'Unknown') for entity in entities]
        if len(entity_names) <= 3:
            combined_names = ", ".join(entity_names)
            simulation_name = f"{interaction_type.capitalize()} interaction: {combined_names}"
        else:
            simulation_name = f"{interaction_type.capitalize()} interaction with {len(entity_names)} entities"
    
    # Save the simulation
    simulation_id = storage.save_simulation(
        context_id=context_id,
        interaction_type=interaction_type,
        entity_ids=entity_ids,
        content=content,
        metadata=metadata,
        final_turn_number=final_turn_number,
        name=simulation_name
    )
    
    # Return the result
    return success_response({
        "id": simulation_id,
        "context_id": context_id,
        "result": content,
        "interaction_type": interaction_type,
        "entity_count": len(entities),
        "final_turn_number": final_turn_number
    })

@app.route('/api/unified-simulations/<simulation_id>', methods=['GET'])
@handle_exceptions
def get_unified_simulation(simulation_id):
    """
    Retrieve a simulation created with the unified simulation system.
    
    Args:
        simulation_id: The ID of the simulation to retrieve
        
    Returns:
        JSON response with the simulation details
    """
    logger = logging.getLogger('app')
    logger.debug(f"Retrieving simulation with ID: {simulation_id}")
    
    # Get the simulation from storage
    simulation = storage.get_simulation(simulation_id)
    
    if not simulation:
        logger.warning(f"Simulation with ID {simulation_id} not found")
        return error_response(f"Simulation with ID {simulation_id} not found", 404)
    
    logger.debug(f"Retrieved simulation data: {json.dumps(simulation, default=str)}")
    
    # Get the context
    context = storage.get_context(simulation['context_id'])
    
    # Get the entities
    entities = []
    for entity_id in simulation['entity_ids']:
        entity = storage.get_entity(entity_id)
        if entity:
            entities.append({
                "id": entity_id,
                "name": entity.get('name', 'Unknown'),
                "description": entity.get('description', '')
            })
    
    # Extract final_turn_number, ensuring it's an integer
    final_turn_number = 0
    if 'final_turn_number' in simulation:
        try:
            final_turn_number = int(simulation['final_turn_number'])
            logger.debug(f"Final turn number from simulation: {final_turn_number}")
        except (ValueError, TypeError):
            logger.warning(f"Invalid final_turn_number in simulation: {simulation.get('final_turn_number')}")
    else:
        logger.warning("No final_turn_number found in simulation data")
    
    # Determine if this was a unified simulation (we could add a flag in the metadata)
    # For now, include all simulations in the response
    
    return success_response({
        "id": simulation_id,
        "context": context['description'] if context else "",
        "context_id": simulation['context_id'],
        "interaction_type": simulation['interaction_type'],
        "result": simulation['content'],
        "entities": entities,
        "created_at": simulation.get('timestamp', ''),
        "metadata": simulation.get('metadata', {}),
        "final_turn_number": final_turn_number
    })

@app.route('/api/unified-simulations/<simulation_id>', methods=['DELETE'])
@handle_exceptions
def delete_unified_simulation(simulation_id):
    """
    Delete a simulation created with the unified simulation system.
    
    Args:
        simulation_id: The ID of the simulation to delete
        
    Returns:
        JSON response indicating success or failure
    """
    logger = logging.getLogger('app')
    logger.info(f"Deleting simulation with ID: {simulation_id}")
    
    # Check if the simulation exists
    simulation = storage.get_simulation(simulation_id)
    if not simulation:
        logger.warning(f"Simulation with ID {simulation_id} not found")
        return error_response(f"Simulation with ID {simulation_id} not found", 404)
    
    # Delete the simulation
    try:
        success = storage.delete_simulation(simulation_id)
        if success:
            logger.info(f"Successfully deleted simulation {simulation_id}")
            return success_response({"message": f"Simulation {simulation_id} deleted successfully"})
        else:
            logger.error(f"Failed to delete simulation {simulation_id}")
            return error_response(f"Failed to delete simulation {simulation_id}", 500)
    except Exception as e:
        logger.exception(f"Error deleting simulation {simulation_id}: {str(e)}")
        return error_response(f"Error deleting simulation: {str(e)}", 500)

@app.route('/api/unified-simulations', methods=['GET'])
@handle_exceptions
def get_unified_simulations():
    """
    Retrieve a list of all simulations.
    
    Can be filtered using query parameters:
        entity_id: Filter by entity ID
        entity_type_id: Filter by entity type ID
        interaction_type: Filter by interaction type (solo, dyadic, group)
        limit: Maximum number of simulations to return (default: 20)
        offset: Number of simulations to skip (for pagination)
    
    Returns:
        JSON response with the list of simulations
    """
    # Get query parameters
    entity_id = request.args.get('entity_id')
    entity_type_id = request.args.get('entity_type_id')
    interaction_type = request.args.get('interaction_type')
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    
    logger.info(f"Getting unified simulations with params: entity_id={entity_id}, entity_type_id={entity_type_id}, interaction_type={interaction_type}, limit={limit}, offset={offset}")
    
    # Get all simulations directly from the database to verify they exist
    try:
        conn = sqlite3.connect(storage.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM simulations")
        count = cursor.fetchone()[0]
        logger.info(f"Database contains {count} simulations")
        
        if count > 0:
            cursor.execute("SELECT id, timestamp, name FROM simulations LIMIT 5")
            sample = cursor.fetchall()
            logger.info(f"Sample simulations: {sample}")
    except Exception as e:
        logger.error(f"Error checking database directly: {str(e)}")
    finally:
        conn.close()
    
    # Try get_all_simulations instead of get_simulations
    try:
        simulations = storage.get_all_simulations()
        logger.info(f"Retrieved {len(simulations)} simulations from get_all_simulations")
    except Exception as e:
        logger.error(f"Error using get_all_simulations: {str(e)}")
        # Fall back to get_simulations
        simulations = storage.get_simulations(
            entity_id=entity_id,
            entity_type_id=entity_type_id,
            interaction_type=interaction_type,
            limit=limit,
            offset=offset
        )
        logger.info(f"Retrieved {len(simulations)} simulations from get_simulations")
    
    # Format the response
    result = []
    for sim in simulations:
        logger.info(f"Processing simulation: {sim.get('id')}")
        try:
            # Get the context
            context_id = sim.get('context_id')
            if context_id:
                context = storage.get_context(context_id)
            else:
                context = None
            
            # Get entity names
            entity_names = []
            entity_ids = sim.get('entity_ids', [])
            if isinstance(entity_ids, str):
                try:
                    entity_ids = json.loads(entity_ids)
                except:
                    entity_ids = []
            
            for entity_id in entity_ids:
                entity = storage.get_entity(entity_id)
                if entity:
                    entity_names.append(entity.get('name', 'Unknown'))
            
            result.append({
                "id": sim.get('id'),
                "context_id": sim.get('context_id'),
                "context": context.get('description', '') if context else "",
                "interaction_type": sim.get('interaction_type'),
                "entity_ids": entity_ids,
                "entity_names": entity_names,
                "created_at": sim.get('timestamp', ''),
                "summary": sim.get('metadata', {}).get('summary', ''),
                "final_turn_number": sim.get('final_turn_number', 0),
                "name": sim.get('name', f"Simulation {sim.get('timestamp', '')[:10]}")
            })
        except Exception as e:
            logger.error(f"Error processing simulation {sim.get('id')}: {str(e)}")
            logger.exception("Exception details:")
    
    logger.info(f"Returning {len(result)} formatted simulations")
    return success_response(result)

@app.route('/api/unified-simulations/<simulation_id>/continue', methods=['POST'])
@handle_exceptions
def continue_unified_simulation(simulation_id):
    """
    Continue an existing simulation with more turns.
    
    Args:
        simulation_id: The ID of the simulation to continue
        
    Returns:
        JSON response with the updated simulation
    """
    logger = logging.getLogger('app')
    logger.info(f"Continuing simulation: {simulation_id}")
    
    # Get the simulation data from storage
    simulation = storage.get_simulation(simulation_id)
    
    if not simulation:
        return error_response(f"Simulation with ID {simulation_id} not found", 404)
    
    # Parse request data
    data = request.json
    n_turns = data.get('n_turns', 1)
    simulation_rounds = data.get('simulation_rounds', 1)
    
    # Get the context
    context = storage.get_context(simulation['context_id'])
    if not context:
        return error_response(f"Context not found for simulation {simulation_id}", 404)
    
    # Get the entities
    entities = []
    for entity_id in simulation['entity_ids']:
        entity = storage.get_entity(entity_id)
        if entity:
            entities.append(entity)
    
    # Set up the last turn number from the simulation
    # This might be missing if the database schema was updated
    try:
        last_turn_number = int(simulation.get('final_turn_number', 0))
        logger.debug(f"Last turn number from database: {last_turn_number}")
    except (ValueError, TypeError):
        # If final_turn_number is invalid, try to extract it from the content
        logger.warning(f"Invalid or missing final_turn_number for simulation {simulation_id}, extracting from content")
        last_turn_number = 0
        content = simulation.get('content', '')
        # Try to find the last turn number in the content
        turn_matches = re.findall(r'TURN (\d+)', content)
        if turn_matches:
            try:
                last_turn_number = int(turn_matches[-1])
                logger.debug(f"Extracted last turn number from content: {last_turn_number}")
            except (ValueError, IndexError):
                logger.warning("Failed to extract valid turn number from content")
    
    # Initialize simulator
    from llm.interaction_module import InteractionSimulator
    simulator = InteractionSimulator()
    
    # Continue the simulation
    final_content = simulation.get('content', '')
    final_turn_number = last_turn_number
    
    # Make a copy of the metadata to avoid modifying the original
    metadata = copy.deepcopy(simulation.get('metadata', {}) or {})
    
    context_str = context.get('description', '')
    
    for _ in range(simulation_rounds):
        logger.debug(f"Starting simulation round with last_turn_number={final_turn_number}")
        result = simulator.forward(
            entities=entities,
            context=context_str,
            n_turns=n_turns,
            last_turn_number=final_turn_number,
            previous_interaction=final_content
        )
        
        # Append the new content
        if final_content and not final_content.endswith('\n\n'):
            final_content += '\n\n'
        final_content += result.content
        
        # Update the final turn number
        final_turn_number = int(result.final_turn_number)
        logger.debug(f"Updated final_turn_number to {final_turn_number}")
    
    # Update the metadata to include rounds and turns info
    if 'simulation_rounds' not in metadata:
        metadata['simulation_rounds'] = 0
    metadata['simulation_rounds'] += simulation_rounds
    
    if 'total_turns' not in metadata:
        metadata['total_turns'] = 0
    metadata['total_turns'] += n_turns * simulation_rounds
    
    # Update the simulation in storage
    try:
        updated_simulation = storage.update_simulation(
            simulation_id=simulation_id,
            content=final_content,
            metadata=metadata,
            final_turn_number=final_turn_number
        )
        
        logger.info(f"Successfully updated simulation {simulation_id} with final_turn_number={final_turn_number}")
        
        # Return the updated simulation with the correct final_turn_number
        return success_response({
            "id": simulation_id,
            "context_id": simulation['context_id'],
            "result": final_content,
            "interaction_type": simulation['interaction_type'],
            "entity_count": len(entities),
            "final_turn_number": final_turn_number
        })
        
    except sqlite3.OperationalError as e:
        # If the error is about the final_turn_number column not existing
        if 'no such column: final_turn_number' in str(e):
            logger.warning(f"final_turn_number column missing: {str(e)}")
            
            # Simply update without the final_turn_number
            metadata['final_turn_number'] = final_turn_number  # Store in metadata instead
            
            try:
                storage.update_simulation(
                    simulation_id=simulation_id,
                    content=final_content,
                    metadata=metadata
                )
                
                logger.info(f"Updated simulation {simulation_id} without final_turn_number column (stored in metadata)")
                
                # Return the response with the final_turn_number even though it wasn't stored in the column
                return success_response({
                    "id": simulation_id,
                    "context_id": simulation['context_id'],
                    "result": final_content,
                    "interaction_type": simulation['interaction_type'],
                    "entity_count": len(entities),
                    "final_turn_number": final_turn_number
                })
                
            except Exception as inner_e:
                logger.error(f"Error updating simulation without final_turn_number: {str(inner_e)}")
                return error_response(f"Error updating simulation: {str(inner_e)}", 500)
        else:
            # Re-raise if it's a different operational error
            logger.error(f"SQLite error: {str(e)}")
            return error_response(f"Database error: {str(e)}", 500)

@app.route('/api/entity-types/<entity_type_id>', methods=['DELETE'])
@handle_exceptions
def delete_entity_type(entity_type_id):
    """
    Delete an entity type by ID.
    
    Args:
        entity_type_id: ID of the entity type
        
    Returns:
        JSON response indicating success or failure
    """
    # Check if entity type exists
    entity_type = storage.get_entity_type(entity_type_id)
    if not entity_type:
        return error_response(f"Entity type with ID {entity_type_id} not found", 404)
    
    success = storage.delete_entity_type(entity_type_id)
    
    if success:
        logger.info(f"Deleted entity type: {entity_type_id}")
        return success_response({"message": f"Entity type {entity_type_id} deleted successfully"})
    else:
        logger.error(f"Failed to delete entity type: {entity_type_id}")
        return error_response("Failed to delete entity type", 500)

@app.route('/api/settings', methods=['GET'])
@handle_exceptions
def get_settings():
    """
    Get the application settings from the config file.
    
    Returns:
        A JSON response with the settings data.
    """
    try:
        # Use the correct path relative to the project root
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'llm_settings.json')
        logger.info(f"Loading settings from: {config_path}")
        
        # Default settings structure
        default_settings = {
            "model_settings": {
                "model": os.environ.get('DSPY_MODEL', 'gpt-4o-mini'),
                "temperature": 1.0,
                "max_tokens": 1000,
                "cache": False,
                "cache_in_memory": False,
                "provider": "openai" # Default provider
            }
        }
        
        # Check if file exists
        if not os.path.exists(config_path):
            logger.info("Settings file doesn't exist, creating with defaults")
            # Save default settings
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(default_settings, f, indent=2)
            return jsonify(default_settings)
        
        # Read the settings from the config file
        with open(config_path, 'r') as f:
            settings = json.load(f)
        
        # Fix nested data structure if it exists
        if 'data' in settings and isinstance(settings['data'], dict):
            if 'model_settings' in settings['data']:
                settings['model_settings'] = settings['data']['model_settings']
            if 'status' in settings['data']:
                del settings['data']['status']
            del settings['data']
        
        # Ensure we have the model_settings property
        if 'model_settings' not in settings:
            logger.info("Adding missing model_settings to loaded settings")
            settings['model_settings'] = default_settings['model_settings']
        
        # Add provider field if missing
        if 'provider' not in settings['model_settings']:
            # Determine provider based on model
            model = settings['model_settings']['model']
            if model.startswith('claude'):
                settings['model_settings']['provider'] = 'anthropic'
            else:
                settings['model_settings']['provider'] = 'openai'
        
        # Clean up any extraneous fields
        if 'status' in settings:
            del settings['status']
            
        # Save the cleaned structure back to the file
        with open(config_path, 'w') as f:
            json.dump(settings, f, indent=2)
            
        logger.info(f"Returning settings: {json.dumps(settings)}")
        # Return directly without nesting
        return jsonify(settings)
    except Exception as e:
        logger.error(f"Error reading settings: {str(e)}")
        # Return a default settings object instead of an error
        default_settings = {
            "model_settings": {
                "model": os.environ.get('DSPY_MODEL', 'gpt-4o-mini'),
                "temperature": 1.0,
                "max_tokens": 1000,
                "cache": False,
                "cache_in_memory": False,
                "provider": "openai"
            }
        }
        return jsonify(default_settings)

@app.route('/api/settings', methods=['POST'])
@handle_exceptions
def update_settings():
    """
    Update the application settings in the config file.
    
    Returns:
        A JSON response indicating success or failure.
    """
    try:
        # Get the settings from the request body
        settings = request.json
        logger.info(f"Received settings update: {json.dumps(settings)}")
        
        # Validate settings
        if 'model_settings' not in settings:
            return jsonify({"error": "Invalid settings: 'model_settings' field is required"}), 400
        
        model_settings = settings['model_settings']
        if 'model' not in model_settings:
            return jsonify({"error": "Invalid settings: 'model' field is required"}), 400
        
        # Ensure model is one of the allowed values
        allowed_models = ['gpt-4o-mini', 'gpt-4o', 'anthropic/claude-3-5-haiku-20241022']
        if model_settings['model'] not in allowed_models:
            return jsonify({"error": f"Invalid model: must be one of {', '.join(allowed_models)}"}), 400
        
        # Determine provider based on model
        if model_settings['model'] == 'anthropic/claude-3-5-haiku-20241022':
            provider = 'anthropic'
            # Check if CLAUDE_API_KEY is available
            if not os.environ.get('CLAUDE_API_KEY'):
                return jsonify({"error": "CLAUDE_API_KEY not found in environment variables"}), 400
        else:
            provider = 'openai'
            # Check if OPENAI_API_KEY is available
            if not os.environ.get('OPENAI_API_KEY'):
                return jsonify({"error": "OPENAI_API_KEY not found in environment variables"}), 400
        
        # Update the environment variable for immediate effect
        if model_settings['model'] == 'anthropic/claude-3-5-haiku-20241022':
            os.environ['DSPY_MODEL'] = model_settings['model']
        else:
            os.environ['DSPY_MODEL'] = model_settings['model']
        
        # Use the correct path relative to the project root
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'llm_settings.json')
        
        # Make sure config directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Clean settings object before saving
        clean_settings = {
            "model_settings": {
                "model": model_settings['model'],
                "temperature": model_settings.get('temperature', 1.0),
                "max_tokens": model_settings.get('max_tokens', 1000),
                "cache": model_settings.get('cache', False),
                "cache_in_memory": model_settings.get('cache_in_memory', False),
                "provider": provider
            }
        }
        
        # Write the settings to the config file
        with open(config_path, 'w') as f:
            json.dump(clean_settings, f, indent=2)
        
        logger.info(f"Updated settings: {json.dumps(clean_settings)}")
        return jsonify({"message": "Settings updated successfully"})
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        return jsonify({"error": f"Failed to update settings: {str(e)}"}), 400

@app.route('/api/entity-types/suggest-dimensions', methods=['POST'])
@handle_exceptions
def suggest_entity_type_dimensions():
    """
    Generate dimensions for an entity type based on name and description.
    
    Request body:
        name: Name of the entity type
        description: Description of the entity type
        n_dimensions: Number of dimensions to generate (optional, default: 5)
        normalize: Whether to normalize dimensions for API compatibility (optional, default: True)
        
    Returns:
        JSON response with the generated dimensions
    """
    data = request.json
    
    # Validate required fields
    if not data or not data.get('name'):
        return error_response("Entity type name is required")
    
    # Get parameters from request
    entity_type_name = data.get('name')
    entity_type_description = data.get('description', '')
    n_dimensions = data.get('n_dimensions', 5)
    normalize = data.get('normalize', True)
    
    # Validate n_dimensions
    if not isinstance(n_dimensions, int) or n_dimensions < 1:
        return error_response("n_dimensions must be a positive integer")
    
    # Generate dimensions
    dimensions = generate_entity_type_dimensions(
        entity_type_name=entity_type_name,
        entity_type_description=entity_type_description,
        n_dimensions=n_dimensions,
        normalize=normalize
    )
    
    # Return success response with dimensions
    return success_response({
        "name": entity_type_name,
        "description": entity_type_description,
        "dimensions": dimensions
    })

@app.route('/api/entity-types/generate-and-create', methods=['POST'])
@handle_exceptions
def generate_and_create_entity_type():
    """
    Generate dimensions and create a new entity type in one step.
    
    Request body:
        name: Name of the entity type
        description: Description of the entity type
        n_dimensions: Number of dimensions to generate (optional, default: 5)
        
    Returns:
        JSON response with the created entity type ID and dimensions
    """
    data = request.json
    
    # Validate required fields
    if not data or not data.get('name'):
        return error_response("Entity type name is required")
    
    # Get parameters from request
    entity_type_name = data.get('name')
    entity_type_description = data.get('description', '')
    n_dimensions = data.get('n_dimensions', 5)
    
    # Validate n_dimensions
    if not isinstance(n_dimensions, int) or n_dimensions < 1:
        return error_response("n_dimensions must be a positive integer")
    
    # Generate normalized dimensions
    dimensions = generate_entity_type_dimensions(
        entity_type_name=entity_type_name,
        entity_type_description=entity_type_description,
        n_dimensions=n_dimensions,
        normalize=True
    )
    
    # Create the entity type
    entity_type_id = storage.save_entity_type(entity_type_name, entity_type_description, dimensions)
    
    # Return success response with entity type ID and dimensions
    return success_response({
        "id": entity_type_id,
        "name": entity_type_name,
        "description": entity_type_description,
        "dimensions": dimensions
    })

if __name__ == '__main__':
    # Use environment variable for port or default to 5001 (avoiding common 5000 port)
    port = int(os.environ.get('BACKEND_PORT', 5001))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask server on {host}:{port} (debug={debug})")
    app.run(debug=debug, host=host, port=port) 