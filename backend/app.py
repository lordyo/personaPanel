"""
Main Flask application for the Entity Simulation Framework.

This module initializes the Flask application, configures it, and defines
the routes for the API endpoints.
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import dspy

# Import modules
from core.entity import EntityType, EntityInstance, Dimension
from core.simulation import SimulationEngine, Context, InteractionType
from llm.dspy_modules import EntityGenerator, SoloInteractionSimulator
import storage as storage
from core.templates import get_template_names, get_template

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize database
@app.before_first_request
def initialize():
    storage.init_db()

# Initialize LLM
lm = None
try:
    # Use the OpenAI API key from environment variables
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        lm = dspy.OpenAI(api_key=api_key)
        dspy.configure(lm=lm)
    else:
        print("Warning: No OPENAI_API_KEY found in environment variables.")
except Exception as e:
    print(f"Warning: Failed to initialize LLM: {e}")
    print("The application will start, but simulation features will not work without a valid LLM configuration.")

# Initialize simulation modules
solo_simulator = None
if lm:
    solo_simulator = SoloInteractionSimulator()

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API is running."""
    return jsonify({
        'status': 'ok',
        'message': 'Entity Simulation Framework API is running'
    })

# Entity Type endpoints
@app.route('/api/entity-types', methods=['GET'])
def get_entity_types():
    """Get all entity types."""
    try:
        entity_types = storage.get_all_entity_types()
        return jsonify(entity_types)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/entity-types', methods=['POST'])
def create_entity_type():
    """Create a new entity type."""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        name = data.get('name')
        description = data.get('description', '')
        dimensions = data.get('dimensions', [])
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        if not dimensions:
            return jsonify({'error': 'At least one dimension is required'}), 400
            
        entity_type_id = storage.save_entity_type(name, description, dimensions)
        return jsonify({'id': entity_type_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/entity-types/<entity_type_id>', methods=['GET'])
def get_entity_type(entity_type_id):
    """Get an entity type by ID."""
    try:
        entity_type = storage.get_entity_type(entity_type_id)
        if entity_type is None:
            return jsonify({'error': 'Entity type not found'}), 404
        return jsonify(entity_type)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Entity endpoints
@app.route('/api/entities', methods=['POST'])
def create_entity():
    """Create a new entity."""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        entity_type_id = data.get('entity_type_id')
        name = data.get('name')
        attributes = data.get('attributes', {})
        
        if not entity_type_id:
            return jsonify({'error': 'Entity type ID is required'}), 400
        if not name:
            return jsonify({'error': 'Name is required'}), 400
            
        entity_id = storage.save_entity(entity_type_id, name, attributes)
        return jsonify({'id': entity_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/entities/<entity_id>', methods=['GET'])
def get_entity(entity_id):
    """Get an entity by ID."""
    try:
        entity = storage.get_entity(entity_id)
        if entity is None:
            return jsonify({'error': 'Entity not found'}), 404
        return jsonify(entity)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/entity-types/<entity_type_id>/entities', methods=['GET'])
def get_entities_by_type(entity_type_id):
    """Get all entities of a specific type."""
    try:
        entities = storage.get_entities_by_type(entity_type_id)
        return jsonify(entities)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Simulation endpoints
@app.route('/api/simulations', methods=['POST'])
def create_simulation():
    """Run a new simulation."""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        context_description = data.get('context')
        entity_ids = data.get('entity_ids', [])
        interaction_type = data.get('interaction_type', 'solo')
        
        if not context_description:
            return jsonify({'error': 'Context is required'}), 400
        if not entity_ids:
            return jsonify({'error': 'At least one entity is required'}), 400
            
        # Save context
        context_id = storage.save_context(context_description)
        
        # Get entities
        entities = []
        entity_names = []
        for entity_id in entity_ids:
            entity = storage.get_entity(entity_id)
            if entity:
                entities.append(entity)
                entity_names.append(entity.get('name', 'Unknown Entity'))
        
        # Check if we have the right number of entities for the interaction type
        if interaction_type == 'solo' and len(entities) != 1:
            return jsonify({'error': 'Solo interaction requires exactly one entity'}), 400
        if interaction_type == 'dyadic' and len(entities) != 2:
            return jsonify({'error': 'Dyadic interaction requires exactly two entities'}), 400
        if interaction_type == 'group' and len(entities) < 2:
            return jsonify({'error': 'Group interaction requires at least two entities'}), 400
        
        # Generate content using DSPy if available
        content = ""
        if interaction_type == 'solo' and solo_simulator and lm:
            # Use the LLM simulator for solo interactions
            try:
                entity = entities[0]
                result = solo_simulator(entity=entity, context=context_description)
                content = result
            except Exception as e:
                print(f"LLM simulation error: {e}")
                # Fallback to placeholder content
                content = f"Solo simulation for {entity_names[0]} in context: {context_description}"
        else:
            # Fallback to placeholder content for other interaction types or if LLM is not available
            if interaction_type == 'solo':
                content = f"Solo simulation for {entity_names[0]} in context: {context_description}"
            elif interaction_type == 'dyadic':
                content = f"Dyadic simulation between {entity_names[0]} and {entity_names[1]} in context: {context_description}"
            else:
                content = f"Group simulation with {', '.join(entity_names)} in context: {context_description}"
        
        # Save simulation with additional metadata
        simulation_id = storage.save_simulation(
            context_id=context_id,
            interaction_type=interaction_type,
            entity_ids=entity_ids,
            content=content,
            metadata={"entity_names": entity_names}
        )
        
        # Prepare response with entity names
        return jsonify({
            'id': simulation_id,
            'content': content,
            'entity_names': entity_names
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulations/<simulation_id>', methods=['GET'])
def get_simulation(simulation_id):
    """Get a simulation by ID."""
    try:
        simulation = storage.get_simulation(simulation_id)
        if simulation is None:
            return jsonify({'error': 'Simulation not found'}), 404
            
        # Add context information
        if simulation.get('context_id'):
            context = storage.get_context(simulation['context_id'])
            simulation['context'] = context
            
        # Extract entity names from metadata if available
        if simulation.get('metadata') and 'entity_names' in simulation['metadata']:
            simulation['entity_names'] = simulation['metadata']['entity_names']
            
        return jsonify(simulation)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulations', methods=['GET'])
def get_simulations():
    """Get all simulations."""
    try:
        simulations = storage.get_all_simulations()
        
        # Enhance response with context descriptions and entity names
        for simulation in simulations:
            # Add context information
            if simulation.get('context_id'):
                context = storage.get_context(simulation['context_id'])
                simulation['context'] = context
                
            # Extract entity names from metadata if available
            if simulation.get('metadata') and 'entity_names' in simulation['metadata']:
                simulation['entity_names'] = simulation['metadata']['entity_names']
                
        return jsonify(simulations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Template endpoints
@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get a list of available entity templates."""
    try:
        templates = get_template_names()
        return jsonify({
            'status': 'success',
            'data': templates
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/templates/<template_id>', methods=['GET'])
def get_template_details(template_id):
    """Get details for a specific template."""
    try:
        template = get_template(template_id)
        if not template:
            return jsonify({
                'status': 'error',
                'message': f'Template with id {template_id} not found'
            }), 404
            
        return jsonify({
            'status': 'success',
            'data': template
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/templates/<template_id>/create', methods=['POST'])
def create_entity_type_from_template(template_id):
    """Create a new entity type based on a template."""
    try:
        template = get_template(template_id)
        if not template:
            return jsonify({
                'status': 'error',
                'message': f'Template with id {template_id} not found'
            }), 404
            
        # Get customization data from request
        data = request.json
        name = data.get('name', template['name'])
        description = data.get('description', template['description'])
        
        # Get dimensions from template, potentially customized by request
        dimensions = template['dimensions']
        
        # Handle customization of dimensions if provided
        if 'dimensions' in data:
            custom_dimensions = data['dimensions']
            # This is a simplified approach - in a real implementation, you might
            # want to merge the customizations with the template dimensions more carefully
            for i, dimension in enumerate(dimensions):
                if i < len(custom_dimensions) and custom_dimensions[i]:
                    # Update any non-null properties from the customization
                    for key, value in custom_dimensions[i].items():
                        if value is not None:
                            dimensions[i].__dict__[key] = value
        
        # Convert dimensions to the format expected by save_entity_type
        dimension_dicts = [
            {
                'name': d.name,
                'description': d.description,
                'type': d.type,
                'options': d.options,
                'min_value': d.min_value,
                'max_value': d.max_value,
                'distribution': d.distribution
            }
            for d in dimensions
        ]
        
        # Create the entity type
        entity_type_id = storage.save_entity_type(name, description, dimension_dicts)
        
        # Return the created entity type
        return jsonify({
            'status': 'success',
            'data': {
                'id': entity_type_id,
                'name': name,
                'description': description,
                'dimensions': dimension_dicts
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 