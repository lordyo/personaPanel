#!/usr/bin/env python3
"""
Script to identify and fix corrupted entity data in the database.

This script addresses the common 'Extra data' JSON validation errors by:
1. Listing all entity types with potentially corrupted data
2. Providing options to fix or clean up corrupted entity types
3. Fixing the attributes/description swap issue for existing entities
"""

import os
import sqlite3
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'entity_sim.db')

def list_entity_types():
    """List all entity types in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name FROM entity_types')
    entity_types = cursor.fetchall()
    
    conn.close()
    return entity_types

def check_entity_type_data(entity_type_id):
    """Check if an entity type has corrupted entity data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, attributes, description FROM entities WHERE entity_type_id = ?', (entity_type_id,))
    entities = cursor.fetchall()
    
    conn.close()
    
    corrupted = []
    valid = []
    
    for entity_id, name, attributes_json, description in entities:
        try:
            json.loads(attributes_json)
            valid.append((entity_id, name))
        except json.JSONDecodeError as e:
            corrupted.append((entity_id, name, attributes_json, description, str(e)))
    
    return valid, corrupted

def fix_swapped_fields(entity_id, attributes_json, description):
    """Fix entities where attributes and description were swapped."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if it's a description-like text in the attributes field
        is_likely_swapped = len(attributes_json) > 5 and attributes_json[0] != '{' and attributes_json[0] != '['
        
        if is_likely_swapped:
            # Swap the attributes and description fields
            cursor.execute(
                'UPDATE entities SET attributes = ?, description = ? WHERE id = ?', 
                ('{}', attributes_json, entity_id)
            )
            logger.info(f"Fixed entity {entity_id} by swapping attributes and description")
        else:
            # Just set attributes to empty dict
            cursor.execute(
                'UPDATE entities SET attributes = ? WHERE id = ?', 
                ('{}', entity_id)
            )
            logger.info(f"Fixed entity {entity_id} by replacing corrupted attributes with empty dict")
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to fix entity {entity_id}: {e}")
        conn.rollback()
        conn.close()
        return False

def main():
    """Main function to identify and fix corrupted entity data."""
    logger.info("Starting database corruption check")
    
    if not os.path.exists(DB_PATH):
        logger.error(f"Database file not found at {DB_PATH}")
        return
    
    entity_types = list_entity_types()
    logger.info(f"Found {len(entity_types)} entity types")
    
    corrupted_types = []
    entity_counts = {}
    
    for entity_type_id, entity_type_name in entity_types:
        valid, corrupted = check_entity_type_data(entity_type_id)
        entity_counts[entity_type_name] = len(valid)
        
        if corrupted:
            logger.warning(f"Entity type '{entity_type_name}' ({entity_type_id}) has {len(corrupted)} corrupted entities")
            corrupted_types.append((entity_type_id, entity_type_name, corrupted))
        else:
            logger.info(f"Entity type '{entity_type_name}' has {len(valid)} valid entities")
    
    # Summarize findings
    print("\nEntity Type Counts:")
    for name, count in entity_counts.items():
        print(f"- '{name}': {count} valid entities")
    
    if not corrupted_types:
        logger.info("No corrupted entity types found!")
        return
    
    logger.info(f"Found {len(corrupted_types)} entity types with corrupted entities")
    
    for entity_type_id, entity_type_name, corrupted_entities in corrupted_types:
        print(f"\nEntity type: {entity_type_name} ({entity_type_id})")
        print(f"Corrupted entities: {len(corrupted_entities)}")
        
        answer = input("Do you want to fix these entities? [y/N]: ").lower()
        if answer == 'y':
            fixed_count = 0
            for entity_id, entity_name, attributes_json, description, error in corrupted_entities:
                logger.info(f"Attempting to fix entity '{entity_name}' ({entity_id})")
                if fix_swapped_fields(entity_id, attributes_json, description):
                    fixed_count += 1
            
            logger.info(f"Fixed {fixed_count} out of {len(corrupted_entities)} corrupted entities for type '{entity_type_name}'")
    
    logger.info("Database corruption check complete")

if __name__ == "__main__":
    main() 