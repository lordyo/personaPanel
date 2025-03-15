#!/usr/bin/env python3
"""
Test script for batch simulations with the new interaction_type and language parameters.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Any

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulations.batch_simulator import BatchSimulationConfig, run_batch
from db.storage import get_all_entity_types, get_entities_by_type

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Test batch simulation with new parameters."""
    logger.info("Starting batch simulation test with interaction_type and language parameters")

    # Get all entity types
    entity_types = get_all_entity_types()
    if not entity_types:
        logger.error("No entity types found in the database")
        return

    # Select the first entity type
    entity_type_id = entity_types[0][0]
    entity_type_name = entity_types[0][1]
    logger.info(f"Using entity type: {entity_type_name} (ID: {entity_type_id})")

    # Get entities of this type
    entities = get_entities_by_type(entity_type_id)
    if not entities or len(entities) < 2:
        logger.error(f"Not enough entities found for type {entity_type_name}")
        return

    # Select the first two entities
    entity_ids = [entities[0][0], entities[1][0]]
    entity_names = [entities[0][1], entities[1][1]]
    logger.info(f"Using entities: {entity_names} (IDs: {entity_ids})")

    # Create batch simulation config
    config = BatchSimulationConfig(
        name="Test Batch with Interaction Type and Language",
        description="Testing batch simulation with new parameters",
        entity_ids=entity_ids,
        context="Test conversation to verify interaction_type and language parameters",
        interaction_size=2,
        num_simulations=1,
        n_turns=1,
        simulation_rounds=1,
        metadata={
            "interaction_type": "debate",
            "language": "Spanish"
        }
    )

    # Run the batch simulation
    logger.info("Running batch simulation...")
    batch_id = run_batch(config)
    logger.info(f"Batch simulation completed with ID: {batch_id}")

if __name__ == "__main__":
    main() 