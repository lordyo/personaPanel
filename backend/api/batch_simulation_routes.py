"""
Batch Simulation API Routes

This module provides API endpoints for managing batch simulations.
"""

import os
import json
import logging
from flask import Blueprint, request, current_app, jsonify, send_file, make_response
from functools import wraps
import threading
import io
import csv
from typing import Dict, List, Any, Optional
import time

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
    def run_batch_thread(config, existing_batch_id):
        try:
            # Pass the existing batch ID to avoid creating another batch
            batch_id = run_batch(config, existing_batch_id)
            logger.info(f"Batch simulation completed with ID: {batch_id}")
        except Exception as e:
            logger.error(f"Error running batch simulation: {str(e)}")
            # Make sure to mark the batch as failed if there's an error
            try:
                storage.update_batch_status(existing_batch_id, "failed")
                logger.info(f"Marked batch {existing_batch_id} as failed due to error")
            except Exception as inner_e:
                logger.error(f"Failed to update batch status: {str(inner_e)}")
    
    # Create the batch record first to get an ID
    batch_id = storage.create_simulation_batch(
        name=config.name,
        description=config.description,
        context=config.context,
        metadata=config.metadata
    )
    
    # Start the batch process in a background thread
    thread = threading.Thread(target=run_batch_thread, args=(config, batch_id))
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

@batch_simulation_bp.route('/<batch_id>/export', methods=['GET', 'POST'])
@handle_exceptions
def export_batch_simulation(batch_id):
    """
    Export batch simulation data.
    
    Query parameters (GET) or form data (POST):
        format: Export format (json or csv, default: json)
    """
    # Log detailed request information
    logger.info(f"Export request received: Method={request.method}, URL={request.url}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    # Get format from either query parameters (GET) or form data (POST)
    if request.method == 'POST':
        format_type = request.form.get('format', 'json').lower()
        logger.info(f"POST Export request received for batch {batch_id} in format {format_type}")
        logger.info(f"Form data: {request.form}")
    else:
        format_type = request.args.get('format', 'json').lower()
        logger.info(f"GET Export request received for batch {batch_id} in format {format_type}")
        logger.info(f"Query parameters: {request.args}")
    
    # Get the batch data
    batch = storage.get_simulation_batch(batch_id)
    
    if not batch:
        logger.error(f"Batch simulation with ID {batch_id} not found")
        return error_response(f"Batch simulation with ID {batch_id} not found", 404)
    
    logger.info(f"Batch data retrieved, size: {len(str(batch))} characters")
    
    # Fetch entity information for all entities involved in the simulations
    simulations = batch.get('simulations', [])
    all_entity_ids = set()
    
    # Collect all unique entity IDs from the simulations
    for sim in simulations:
        entity_ids = sim.get('entity_ids', [])
        all_entity_ids.update(entity_ids)
    
    # Fetch detailed entity information
    entity_details = {}
    for entity_id in all_entity_ids:
        entity = storage.get_entity(entity_id)
        if entity:
            entity_details[entity_id] = {
                'id': entity.get('id'),
                'name': entity.get('name'),
                'description': entity.get('description'),
                'attributes': entity.get('attributes', {}),
                'entity_type_id': entity.get('entity_type_id')
            }
    
    logger.info(f"Retrieved details for {len(entity_details)} entities")
    
    # Ensure browsers handle the response as a download, not as a webpage
    # Add a timestamp to make filename unique
    timestamp = str(int(time.time()))
    filename_suffix = f"_{timestamp}" 
    
    if format_type == 'json':
        # Export as JSON
        # Add entity details to the batch data
        enriched_batch = batch.copy()
        enriched_batch['entities'] = entity_details
        
        output = json.dumps(enriched_batch, indent=2)
        
        # Create a memory file-like object
        mem = io.BytesIO()
        mem.write(output.encode('utf-8'))
        mem.seek(0)
        
        logger.info(f"JSON export prepared, sending file attachment: batch_simulation_{batch_id}{filename_suffix}.json")
        
        response = send_file(
            mem,
            mimetype='application/json',
            as_attachment=True,
            download_name=f"batch_simulation_{batch_id}{filename_suffix}.json"
        )
        
        # Add headers to ensure the browser treats this as a download
        response.headers.add('Content-Disposition', f'attachment; filename="batch_simulation_{batch_id}{filename_suffix}.json"')
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Cache-Control', 'no-cache, no-store, must-revalidate')
        response.headers.add('Pragma', 'no-cache')
        response.headers.add('Expires', '0')
        
        return response
    
    elif format_type == 'csv':
        # Export as CSV
        simulations = batch.get('simulations', [])
        
        if not simulations:
            logger.error(f"No simulations found in batch {batch_id}")
            return error_response("No simulations found in this batch", 404)
        
        # Create a memory file-like object for CSV
        mem = io.StringIO()
        writer = csv.writer(mem)
        
        # Write simulation data with enhanced entity information
        writer.writerow([
            'Simulation ID', 'Sequence Number', 'Interaction Type', 
            'Entity IDs', 'Entity Names', 'Entity Descriptions',
            'Context', 'Content', 'Timestamp'
        ])
        
        # Write data for each simulation
        for sim in simulations:
            sim_entity_ids = sim.get('entity_ids', [])
            
            # Compile entity names and descriptions for this simulation
            entity_names = []
            entity_descriptions = []
            
            for entity_id in sim_entity_ids:
                entity = entity_details.get(entity_id, {})
                entity_names.append(entity.get('name', 'Unknown'))
                entity_descriptions.append(entity.get('description', ''))
            
            writer.writerow([
                sim.get('id', ''),
                sim.get('sequence_number', ''),
                sim.get('interaction_type', ''),
                ','.join(sim_entity_ids),
                '|'.join(entity_names),
                '|'.join(entity_descriptions),
                batch.get('context', ''),
                sim.get('content', ''),
                sim.get('timestamp', '')
            ])
        
        # Add a separate section for detailed entity information
        writer.writerow([])  # Empty row as separator
        writer.writerow(['Entity Details'])
        writer.writerow(['Entity ID', 'Name', 'Description', 'Entity Type ID', 'Attributes'])
        
        for entity_id, entity in entity_details.items():
            writer.writerow([
                entity_id,
                entity.get('name', ''),
                entity.get('description', ''),
                entity.get('entity_type_id', ''),
                json.dumps(entity.get('attributes', {}))
            ])
        
        # Convert to bytes for send_file
        mem.seek(0)
        mem_bytes = io.BytesIO()
        mem_bytes.write(mem.getvalue().encode('utf-8'))
        mem_bytes.seek(0)
        
        logger.info(f"CSV export prepared, sending file attachment: batch_simulation_{batch_id}{filename_suffix}.csv")
        
        response = send_file(
            mem_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"batch_simulation_{batch_id}{filename_suffix}.csv"
        )
        
        # Add headers to ensure the browser treats this as a download
        response.headers.add('Content-Disposition', f'attachment; filename="batch_simulation_{batch_id}{filename_suffix}.csv"')
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Cache-Control', 'no-cache, no-store, must-revalidate')
        response.headers.add('Pragma', 'no-cache')
        response.headers.add('Expires', '0')
        
        return response
    
    else:
        logger.error(f"Unsupported export format requested: {format_type}")
        return error_response(f"Unsupported export format: {format_type}", 400)

@batch_simulation_bp.route('/<batch_id>/download', methods=['GET'])
@handle_exceptions
def download_batch_simulation(batch_id):
    """
    Serve a simple HTML page that will automatically download the batch simulation data.
    
    Query parameters:
        format: Export format (json or csv, default: json)
    """
    format_type = request.args.get('format', 'json').lower()
    timestamp = str(int(time.time()))
    
    # Create the download URL with the timestamp
    download_url = f"/api/batch-simulations/{batch_id}/export?format={format_type}&t={timestamp}"
    
    # Create a simple HTML page that will automatically trigger the download
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Downloading Batch Simulation...</title>
        <script>
            // Start download immediately
            window.onload = function() {{
                // Use a short delay to allow the page to load first
                setTimeout(function() {{
                    window.location.href = "{download_url}";
                    
                    // Redirect back to the previous page after a short delay
                    setTimeout(function() {{
                        window.history.back();
                    }}, 1000);
                }}, 100);
            }};
        </script>
    </head>
    <body>
        <h1>Download Starting...</h1>
        <p>Your download should begin automatically. If it doesn't, <a href="{download_url}">click here</a>.</p>
        <p>This page will close automatically...</p>
    </body>
    </html>
    """
    
    response = make_response(html)
    response.headers['Content-Type'] = 'text/html'
    return response 