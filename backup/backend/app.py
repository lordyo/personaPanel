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

# Load environment variables from .env file
load_dotenv()

# Import modules
from core.entity import EntityType, EntityInstance, Dimension
from core.simulation import SimulationEngine, Context, InteractionType
from llm.dspy_modules import EntityGenerator
import storage as storage
from core.templates import get_template_names, get_template
from llm.simulation_modules import SoloInteractionSimulator, DyadicInteractionSimulator, GroupInteractionSimulator, LLMError

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
    
    # Run simulation based on interaction type
    if interaction_type == 'solo':
        simulator = SoloInteractionSimulator()
        prediction = simulator.forward(
            entities[0], 
            context_desc, 
            n_rounds=n_rounds,
            last_round_number=last_round_number,
            previous_interaction=previous_interaction
        )
        # Extract the content from the prediction
        result = prediction.content
    elif interaction_type == 'dyadic':
        simulator = DyadicInteractionSimulator()
        prediction = simulator.forward(
            entities[0], 
            entities[1], 
            context_desc,
            n_rounds=n_rounds,
            last_round_number=last_round_number,
            previous_interaction=previous_interaction
        )
        # Extract the content from the prediction
        result = prediction.content
    else:  # group
        simulator = GroupInteractionSimulator()
        prediction = simulator.forward(
            entities, 
            context_desc,
            n_rounds=n_rounds,
            last_round_number=last_round_number,
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

if __name__ == '__main__':
    # Use environment variable for port or default to 5001 (avoiding common 5000 port)
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask server on {host}:{port} (debug={debug})")
    app.run(debug=debug, host=host, port=port) 