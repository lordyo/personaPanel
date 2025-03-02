#!/usr/bin/env python3

"""
Entity Field Fixer

This script fixes the database issue where the description and attributes fields
have been swapped in the entities table.
"""

import sqlite3
import json
import os
import sys
import logging
from typing import Dict, List, Any, Tuple, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('field_fixer')

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'entity_sim.db')

def connect_db() -> sqlite3.Connection:
    """Connect to the SQLite database."""
    if not os.path.exists(DB_PATH):
        logger.error(f"Database file not found at {DB_PATH}")
        sys.exit(1)
    
    return sqlite3.connect(DB_PATH)

def get_all_entities() -> List[Tuple]:
    """Get all entities from the database."""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, entity_type_id, name, attributes, created_at, description FROM entities')
    entities = cursor.fetchall()
    
    conn.close()
    return entities

def fix_entity_fields(entity_id: str, attributes: str, description: str) -> bool:
    """
    Fix entity fields by swapping description and attributes.
    
    Args:
        entity_id: ID of the entity to fix
        attributes: Current attributes value (should be moved to description)
        description: Current description value (should be moved to attributes)
    
    Returns:
        True if the update was successful, False otherwise
    """
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # First, let's determine what to do with these fields
        new_attributes = description  # Move description to attributes
        new_description = attributes  # Move attributes to description
        
        # If new_attributes isn't valid JSON, convert it to empty object
        try:
            json.loads(new_attributes)
        except (json.JSONDecodeError, TypeError):
            new_attributes = "{}"
        
        cursor.execute(
            'UPDATE entities SET attributes = ?, description = ? WHERE id = ?',
            (new_attributes, new_description, entity_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating entity {entity_id}: {e}")
        conn.rollback()
        conn.close()
        return False

def fix_all_entities():
    """Find and fix all entities with swapped fields."""
    entities = get_all_entities()
    
    fixed_count = 0
    error_count = 0
    
    for entity in entities:
        entity_id, entity_type_id, name, attributes, created_at, description = entity
        
        logger.info(f"Fixing fields for entity {name} ({entity_id})")
        
        if fix_entity_fields(entity_id, attributes, description):
            fixed_count += 1
            logger.info(f"Fixed fields for entity {name} ({entity_id})")
        else:
            error_count += 1
            logger.error(f"Failed to fix fields for entity {name} ({entity_id})")
    
    logger.info(f"Entity field fix complete:")
    logger.info(f"  - {fixed_count} entities fixed")
    logger.info(f"  - {error_count} errors")
    
    return fixed_count, error_count

if __name__ == "__main__":
    logger.info("Starting entity field fixer...")
    
    if not os.path.exists(DB_PATH):
        logger.error(f"Database file not found at {DB_PATH}")
        sys.exit(1)
    
    fixed, errors = fix_all_entities()
    
    if fixed > 0:
        logger.info(f"Successfully fixed {fixed} entities!")
    else:
        logger.warning("No entities were fixed.")
    
    if errors > 0:
        logger.warning(f"There were {errors} errors during the fix process.")
    
    logger.info("Entity field fixing complete.") 