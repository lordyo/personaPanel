"""
Batch Simulation API Routes

This module provides API endpoints for managing batch simulations.
"""

import os
import json
import logging
from flask import Blueprint, request, current_app, jsonify, send_file
from functools import wraps
import threading
import io
import csv
from typing import Dict, List, Any, Optional

import storage
from simulations.batch_simulator import BatchSimulationConfig, run_batch

# Configure logging
logger = logging.getLogger(__name__)

# Create a blueprint for batch simulation routes
batch_simulation_bp = Blueprint('batch_simulation', __name__)

# Response helper functions
def success_response(data, status_code=200):
    """Format a successful response."""
    return jsonify({
        "status": "success",
        "data": data
    }), status_code

def error_response(message, status_code=400):
    """Format an error response."""
    return jsonify({
        "status": "error",
        "message": message
    }), status_code

# Exception handling decorator
def handle_exceptions(func):
    """Decorator to handle exceptions in API routes."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Error in API route {func.__name__}: {str(e)}")
            return error_response(f"Server error: {str(e)}", 500)
    return wrapper

# API Routes

@batch_simulation_bp.route('', methods=['POST'])
@handle_exceptions
def create_batch_simulation():
    """
    Create a new batch simulation.
    
    Request body:
    {
        "name": "Batch Simulation Name",
        "description": "Optional description",
        "context": "Situation context description",
        "entity_ids": ["id1", "id2", "id3", ...],
        "interaction_size": 2,
        "num_simulations": 5,
        "n_turns": 1,
        "simulation_rounds": 1,
        "metadata": { "optional": "metadata" }
    }
    """
    data = request.json or {}
    
    # Validate required fields
    required_fields = ['name', 'context', 'entity_ids', 'interaction_size', 'num_simulations']
    for field in required_fields:
        if field not in data:
            return error_response(f"Missing required field: {field}", 400)
    
    # Validate entity IDs
    if not isinstance(data['entity_ids'], list) or len(data['entity_ids']) == 0:
        return error_response("entity_ids must be a non-empty list", 400)
    
    # Validate interaction_size
    interaction_size = data.get('interaction_size')
    if not isinstance(interaction_size, int) or interaction_size < 1:
        return error_response("interaction_size must be a positive integer", 400)
    
    # Validate num_simulations
    num_simulations = data.get('num_simulations')
    if not isinstance(num_simulations, int) or num_simulations < 1:
        return error_response("num_simulations must be a positive integer", 400)
    
    # Create batch config
    config = BatchSimulationConfig(
        name=data['name'],
        description=data.get('description'),
        entity_ids=data['entity_ids'],
        context=data['context'],
        interaction_size=interaction_size,
        num_simulations=num_simulations,
        n_turns=data.get('n_turns', 1),
        simulation_rounds=data.get('simulation_rounds', 1),
        metadata=data.get('metadata')
    )
    
    # Start batch simulation in a separate thread to avoid blocking the response
    def run_batch_thread(config):
        try:
            batch_id = run_batch(config)
            logger.info(f"Batch simulation completed with ID: {batch_id}")
        except Exception as e:
            logger.error(f"Error running batch simulation: {str(e)}")
    
    # Create the batch record first to get an ID
    batch_id = storage.create_simulation_batch(
        name=config.name,
        description=config.description,
        context=config.context,
        metadata=config.metadata
    )
    
    # Start the batch process in a background thread
    thread = threading.Thread(target=run_batch_thread, args=(config,))
    thread.daemon = True  # Allow the main process to exit even if the thread is still running
    thread.start()
    
    return success_response({
        "id": batch_id,
        "message": "Batch simulation started"
    }, 201)

@batch_simulation_bp.route('', methods=['GET'])
@handle_exceptions
def get_all_batch_simulations():
    """
    Get all batch simulations.
    
    Query parameters:
        include_simulations: Whether to include simulations in each batch (default: false)
    """
    include_simulations = request.args.get('include_simulations', 'false').lower() == 'true'
    
    batches = storage.get_all_simulation_batches(include_simulations)
    
    return success_response(batches)

@batch_simulation_bp.route('/<batch_id>', methods=['GET'])
@handle_exceptions
def get_batch_simulation(batch_id):
    """
    Get a specific batch simulation by ID.
    """
    batch = storage.get_simulation_batch(batch_id)
    
    if not batch:
        return error_response(f"Batch simulation with ID {batch_id} not found", 404)
    
    return success_response(batch)

@batch_simulation_bp.route('/<batch_id>', methods=['DELETE'])
@handle_exceptions
def delete_batch_simulation(batch_id):
    """
    Delete a batch simulation and all its associated simulations.
    """
    result = storage.delete_simulation_batch(batch_id)
    
    if not result:
        return error_response(f"Batch simulation with ID {batch_id} not found or could not be deleted", 404)
    
    return success_response({
        "message": f"Batch simulation {batch_id} deleted successfully"
    })

@batch_simulation_bp.route('/<batch_id>/export', methods=['GET'])
@handle_exceptions
def export_batch_simulation(batch_id):
    """
    Export batch simulation data.
    
    Query parameters:
        format: Export format (json or csv, default: json)
    """
    format_type = request.args.get('format', 'json').lower()
    
    # Get the batch data
    batch = storage.get_simulation_batch(batch_id)
    
    if not batch:
        return error_response(f"Batch simulation with ID {batch_id} not found", 404)
    
    if format_type == 'json':
        # Export as JSON
        output = json.dumps(batch, indent=2)
        
        # Create a memory file-like object
        mem = io.BytesIO()
        mem.write(output.encode('utf-8'))
        mem.seek(0)
        
        return send_file(
            mem,
            mimetype='application/json',
            as_attachment=True,
            download_name=f"batch_simulation_{batch_id}.json"
        )
    
    elif format_type == 'csv':
        # Export as CSV
        simulations = batch.get('simulations', [])
        
        if not simulations:
            return error_response("No simulations found in this batch", 404)
        
        # Create a memory file-like object for CSV
        mem = io.StringIO()
        writer = csv.writer(mem)
        
        # Write header
        writer.writerow([
            'Simulation ID', 'Sequence Number', 'Interaction Type', 
            'Entity IDs', 'Context', 'Content', 'Timestamp'
        ])
        
        # Write data
        for sim in simulations:
            writer.writerow([
                sim.get('id', ''),
                sim.get('sequence_number', ''),
                sim.get('interaction_type', ''),
                ','.join(sim.get('entity_ids', [])),
                batch.get('context', ''),
                sim.get('content', ''),
                sim.get('timestamp', '')
            ])
        
        # Convert to bytes for send_file
        mem.seek(0)
        mem_bytes = io.BytesIO()
        mem_bytes.write(mem.getvalue().encode('utf-8'))
        mem_bytes.seek(0)
        
        return send_file(
            mem_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"batch_simulation_{batch_id}.csv"
        )
    
    else:
        return error_response(f"Unsupported export format: {format_type}", 400) 