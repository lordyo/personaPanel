#!/usr/bin/env python3
"""
Script to create test entities for batch simulation testing.
"""

import os
import sys
import logging
import json

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Create test entities for batch simulation."""
    
    # Get entity types
    entity_types = storage.get_all_entity_types()
    
    if not entity_types:
        logger.error("No entity types found in the database. Please create at least one entity type first.")
        return
    
    # Use the first entity type
    entity_type_id = entity_types[0]['id']
    entity_type_name = entity_types[0]['name']
    logger.info(f"Using entity type: {entity_type_name} (ID: {entity_type_id})")
    
    # Check if dimensions exist
    entity_type = storage.get_entity_type(entity_type_id)
    
    # Load dimensions (might be a JSON string or already parsed)
    dimensions = entity_type.get('dimensions', [])
    if isinstance(dimensions, str):
        try:
            dimensions = json.loads(dimensions)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse dimensions JSON for entity type {entity_type_name}")
            return
    
    if not dimensions:
        logger.error(f"Entity type {entity_type_name} has no dimensions defined")
        return
    
    logger.info(f"Found dimensions: {dimensions}")
    
    # Create test entities with default attribute values
    test_entities = [
        {
            "name": "Test Entity 1",
            "description": "A test entity for batch simulation",
            "attributes": {dim["name"]: 0.5 for dim in dimensions} if isinstance(dimensions, list) else {dim: 0.5 for dim in dimensions}
        },
        {
            "name": "Test Entity 2",
            "description": "Another test entity for batch simulation",
            "attributes": {dim["name"]: 0.7 for dim in dimensions} if isinstance(dimensions, list) else {dim: 0.7 for dim in dimensions}
        }
    ]
    
    entity_ids = []
    for entity_data in test_entities:
        # Check if entity with this name already exists
        existing_entities = storage.get_entities_by_type(entity_type_id)
        exists = False
        for existing in existing_entities:
            if existing['name'] == entity_data['name']:
                logger.info(f"Entity {entity_data['name']} already exists with ID: {existing['id']}")
                entity_ids.append(existing['id'])
                exists = True
                break
        
        if not exists:
            # Create the entity
            entity_id = storage.save_entity(
                entity_type_id=entity_type_id,
                name=entity_data['name'],
                description=entity_data['description'],
                attributes=entity_data['attributes']
            )
            logger.info(f"Created entity {entity_data['name']} with ID: {entity_id}")
            entity_ids.append(entity_id)
    
    logger.info(f"Created/found {len(entity_ids)} test entities")
    return entity_ids

if __name__ == "__main__":
    main() 