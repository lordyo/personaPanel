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

# Load environment variables from .env file
load_dotenv()

# Import modules
from core.entity import EntityType, EntityInstance, Dimension
from core.simulation import SimulationEngine, Context, InteractionType
from llm.dspy_modules import EntityGenerator, SoloInteractionSimulator, DyadicInteractionSimulator, GroupInteractionSimulator, LLMError
import storage as storage
from core.templates import get_template_names, get_template

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS properly - important for cross-origin requests
CORS(app, resources={r"/api/*": {"origins": "*"}})

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
    Decorator to handle exceptions in route handlers.
    
    Args:
        f: Function to decorate
        
    Returns:
        Wrapped function with exception handling
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except LLMError as e:
            logger.error(f"LLM Error: {str(e)}")
            return error_response(f"LLM Error: {str(e)}", 503)
        except ValueError as e:
            logger.error(f"Validation Error: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
            return error_response("An unexpected error occurred", 500)
    return decorated_function

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
    
    # Update the entity type
    storage.update_entity_type(entity_type_id, name, description, dimensions)
    logger.info(f"Updated entity type: {name} (ID: {entity_type_id})")
    
    updated_entity_type = storage.get_entity_type(entity_type_id)
    return success_response(updated_entity_type)

@app.route('/api/entities', methods=['POST'])
@handle_exceptions
def create_entity():
    """
    Create a new entity instance.
    
    Request body:
        entity_type_id: ID of the entity type
        name: Name of the entity
        attributes: Dictionary of attribute values
        generate: Boolean indicating whether to generate attributes using LLM
        variability: Variability level for generation (low, medium, high)
        
    Returns:
        JSON response with the created entity ID
    """
    data = request.json
    
    # Validate required fields
    if not data or not data.get('entity_type_id'):
        return error_response("Entity type ID is required")
    
    entity_type_id = data['entity_type_id']
    entity_type = storage.get_entity_type(entity_type_id)
    
    if not entity_type:
        return error_response(f"Entity type with ID {entity_type_id} not found", 404)
    
    # If 'generate' is true, use LLM to generate entity
    if data.get('generate', False):
        if not lm:
            return error_response("LLM is not configured", 503)
        
        variability = data.get('variability', 'medium')
        if variability not in ['low', 'medium', 'high']:
            return error_response("Variability must be 'low', 'medium', or 'high'")
        
        generator = EntityGenerator()
        generated = generator.forward(
            entity_type['name'],
            entity_type['dimensions'],
            variability
        )
        
        name = generated['name']
        attributes = generated['attributes']
    else:
        # Use provided name and attributes
        name = data.get('name')
        attributes = data.get('attributes', {})
        
        if not name:
            return error_response("Name is required when not generating")
    
    entity_id = storage.save_entity(entity_type_id, name, attributes)
    logger.info(f"Created entity: {name} (ID: {entity_id})")
    
    return success_response({"id": entity_id}, 201)

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
        result = simulator.forward(entities[0], context_desc)
    elif interaction_type == 'dyadic':
        simulator = DyadicInteractionSimulator()
        result = simulator.forward(entities[0], entities[1], context_desc)
    else:  # group
        simulator = GroupInteractionSimulator()
        result = simulator.forward(entities, context_desc)
    
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
            entities.append(entity)
    
    simulation['entities'] = entities
    
    # Get context information
    context = storage.get_context(simulation['context_id'])
    if context:
        simulation['context'] = context
    
    return success_response(simulation)

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
    return success_response(simulations)

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
    dimensions = template.get('dimensions', [])
    
    entity_type_id = storage.save_entity_type(name, description, dimensions)
    logger.info(f"Created entity type from template {template_id}: {name} (ID: {entity_type_id})")
    
    return success_response({"id": entity_type_id}, 201)

if __name__ == '__main__':
    # Use environment variable for port or default to 5001 (avoiding common 5000 port)
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask server on {host}:{port} (debug={debug})")
    app.run(debug=debug, host=host, port=port) 