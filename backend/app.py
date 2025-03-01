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
from backend.core.entity import EntityType, EntityInstance, Dimension
from backend.core.simulation import SimulationEngine, Context, InteractionType
from backend.llm.dspy_modules import EntityGenerator, SoloInteractionSimulator
import backend.storage as storage

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
    # This is a placeholder for the actual LLM initialization
    # In a real implementation, we would initialize the LLM here
    # lm = dspy.LM('openai')
    # dspy.configure(lm=lm)
    pass
except Exception as e:
    print(f"Warning: Failed to initialize LLM: {e}")
    print("The application will start, but simulation features will not work without a valid LLM configuration.")

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
        # This is a placeholder implementation
        # In a real implementation, we would use the LLM to generate content
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
        for entity_id in entity_ids:
            entity = storage.get_entity(entity_id)
            if entity:
                entities.append(entity)
        
        # Check if we have the right number of entities for the interaction type
        if interaction_type == 'solo' and len(entities) != 1:
            return jsonify({'error': 'Solo interaction requires exactly one entity'}), 400
        if interaction_type == 'dyadic' and len(entities) != 2:
            return jsonify({'error': 'Dyadic interaction requires exactly two entities'}), 400
        if interaction_type == 'group' and len(entities) < 2:
            return jsonify({'error': 'Group interaction requires at least two entities'}), 400
        
        # Generate placeholder content (in a real implementation, this would use the LLM)
        if interaction_type == 'solo':
            content = f"Solo simulation for {entities[0]['name']} in context: {context_description}"
        elif interaction_type == 'dyadic':
            content = f"Dyadic simulation between {entities[0]['name']} and {entities[1]['name']} in context: {context_description}"
        else:
            entity_names = [entity['name'] for entity in entities]
            content = f"Group simulation with {', '.join(entity_names)} in context: {context_description}"
        
        # Save simulation
        simulation_id = storage.save_simulation(
            context_id=context_id,
            interaction_type=interaction_type,
            entity_ids=entity_ids,
            content=content
        )
        
        return jsonify({
            'id': simulation_id,
            'content': content
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
        return jsonify(simulation)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulations', methods=['GET'])
def get_simulations():
    """Get all simulations."""
    try:
        simulations = storage.get_all_simulations()
        return jsonify(simulations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 