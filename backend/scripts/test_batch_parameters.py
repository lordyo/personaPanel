#!/usr/bin/env python3
"""
Simple test script for batch simulation with interaction_type and language parameters.
"""

import os
import sys
import logging

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulations.batch_simulator import BatchSimulationConfig, run_batch
import storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run a simple batch simulation with explicit interaction_type and language."""
    
    # Get entity types
    entity_types = storage.get_all_entity_types()
    
    if not entity_types:
        logger.error("No entity types found in the database")
        return None
    
    entity_type_id = entity_types[0]['id']
    logger.info(f"Using entity type: {entity_types[0]['name']}")
    
    # Get entities of this type
    entities = storage.get_entities_by_type(entity_type_id)
    
    if not entities or len(entities) < 2:
        logger.error(f"Not enough entities found for entity type {entity_type_id}")
        return None
    
    # Use the first two entities
    entity_ids = [entities[0]['id'], entities[1]['id']]
    logger.info(f"Using entities: {entities[0]['name']} and {entities[1]['name']}")
    
    # Create batch configuration with explicit metadata
    config = BatchSimulationConfig(
        name="Test Interaction Type and Language",
        description="Testing batch simulation with interaction_type and language parameters",
        entity_ids=entity_ids,
        context="This is a test conversation in a specific language and interaction format.",
        interaction_size=2,
        num_simulations=1,
        n_turns=1,
        simulation_rounds=1,
        metadata={
            "interaction_type": "debate",
            "language": "Spanish"
        }
    )
    
    # Log the configuration
    logger.info(f"Running batch with interaction_type={config.metadata.get('interaction_type')} "
                f"and language={config.metadata.get('language')}")
    
    # Run the batch
    batch_id = run_batch(config)
    
    logger.info(f"Batch simulation completed with ID: {batch_id}")
    return batch_id

if __name__ == "__main__":
    main() 