#!/usr/bin/env python3
"""
Debug batch simulations by running the core functions directly,
bypassing the Flask API to get more detailed error information.
"""

import sys
import os
import json
import time
import logging
import traceback
import sqlite3
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Database path
DB_PATH = "data/entity_sim.db"

def get_entity(entity_id):
    """Get an entity from the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM entities WHERE id = ?', (entity_id,))
        entity_row = cursor.fetchone()
        
        if not entity_row:
            logger.error(f"Entity not found: {entity_id}")
            return None
            
        # Get column names
        columns = [column[0] for column in cursor.description]
        
        # Create entity dict
        entity = dict(zip(columns, entity_row))
        
        # Parse JSON fields
        if 'dimensions' in entity and entity['dimensions']:
            try:
                entity['dimensions'] = json.loads(entity['dimensions'])
            except json.JSONDecodeError:
                logger.error(f"Error parsing dimensions JSON for entity {entity_id}")
                
        conn.close()
        return entity
    except Exception as e:
        logger.error(f"Error getting entity {entity_id}: {str(e)}")
        return None

def get_entity_ids_by_type(entity_type_id, limit=5):
    """Get entity IDs for a specific entity type."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id FROM entities WHERE entity_type_id = ? LIMIT ?', 
            (entity_type_id, limit)
        )
        
        entity_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return entity_ids
    except Exception as e:
        logger.error(f"Error getting entities for type {entity_type_id}: {str(e)}")
        return []

def debug_batch_simulation():
    """Run a debug batch simulation and report detailed errors."""
    try:
        # Import necessary modules from backend
        # We do this here to avoid import errors when the script is first parsed
        from simulations.batch_simulator import run_batch, BatchSimulationConfig
        from simulations.run_simulation import setup_dspy
        
        # First, set up DSPy
        logger.info("Setting up DSPy...")
        setup_dspy()
        
        # Get Swiss HR Professionals entity type ID
        entity_type_id = "106f11c0-52a9-4ff5-9f95-b2b82de8fa11"
        
        # Get some entities
        entity_ids = get_entity_ids_by_type(entity_type_id, limit=1)
        
        if not entity_ids:
            logger.error("No entities found for testing")
            return
            
        logger.info(f"Using entities: {entity_ids}")
        
        # Create batch config
        config = BatchSimulationConfig(
            name=f"DebugBatch_{int(time.time())}",
            description="Debug batch simulation test",
            entity_ids=entity_ids,
            context="This is a test batch with a single entity for debugging purposes.",
            interaction_size=1,  # Solo simulation
            num_simulations=1,
            n_turns=1,
            simulation_rounds=1,
            metadata={"debug": True}
        )
        
        logger.info(f"Created batch config: {config}")
        
        # Run the batch directly
        logger.info("Running batch simulation...")
        batch_id = run_batch(config)
        
        logger.info(f"Batch completed with ID: {batch_id}")
        
        # Check final status
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT status FROM simulation_batches WHERE id = ?', 
            (batch_id,)
        )
        
        status = cursor.fetchone()[0]
        
        logger.info(f"Final batch status: {status}")
        
        # Get any component simulations
        cursor.execute(
            '''
            SELECT s.id 
            FROM simulations s 
            JOIN batch_simulations bs ON s.id = bs.simulation_id
            WHERE bs.batch_id = ?
            ''', 
            (batch_id,)
        )
        
        simulations = cursor.fetchall()
        conn.close()
        
        logger.info(f"Number of component simulations: {len(simulations)}")
        
        return batch_id
        
    except Exception as e:
        logger.error("Error in debug_batch_simulation:")
        logger.error(traceback.format_exc())
        return None

if __name__ == "__main__":
    print("Running debug batch simulation...")
    batch_id = debug_batch_simulation()
    
    if batch_id:
        print(f"Complete. Check the batch with: python3 inspect_batch.py {batch_id}")
    else:
        print("Failed to run batch simulation. Check the logs above for details.") 