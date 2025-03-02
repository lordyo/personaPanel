#!/usr/bin/env python3
"""
Final database cleanup script that ensures all entities have correct attributes.
This script checks all entities and ensures their attributes field contains valid JSON,
moving any JSON from description to attributes if needed.
"""

import os
import sqlite3
import json
import logging
import sys
from typing import Dict, Any, List, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'entity_sim.db')

def connect_db():
    """Connect to the SQLite database."""
    if not os.path.exists(DB_PATH):
        logger.error(f"Database file not found at {DB_PATH}")
        sys.exit(1)
    
    return sqlite3.connect(DB_PATH)

def get_all_entities():
    """Get all entities from the database with their column structure."""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Get column names
    cursor.execute("PRAGMA table_info(entities)")
    columns = [col[1] for col in cursor.fetchall()]
    logger.info(f"Database columns: {columns}")
    
    # Get all entities
    cursor.execute('SELECT * FROM entities')
    entities = cursor.fetchall()
    
    conn.close()
    
    # Return both column names and entity data
    return columns, entities

def fix_entity(entity_id: str, attributes: str, description: str) -> bool:
    """
    Ensure entity fields are correct by validating and fixing the attributes JSON.
    
    Args:
        entity_id: The entity ID
        attributes: Current attributes field value
        description: Current description field value
        
    Returns:
        True if the entity was fixed, False otherwise
    """
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        needs_fix = False
        attr_json = {}
        desc_str = description
        
        # Check if attributes is valid JSON
        try:
            attr_json = json.loads(attributes)
            if isinstance(attr_json, dict) and len(attr_json) > 0:
                # Attributes already valid, no fix needed
                conn.close()
                return False
        except json.JSONDecodeError:
            needs_fix = True
        
        # If attributes is empty or invalid, check description
        if needs_fix or not attr_json:
            try:
                # See if description contains valid JSON that should be attributes
                potential_attr = json.loads(description)
                if isinstance(potential_attr, dict) and len(potential_attr) > 0:
                    # Description contains attributes JSON, move it to attributes
                    attr_json = potential_attr
                    desc_str = ""  # Clear description since it contained attributes
                    needs_fix = True
            except json.JSONDecodeError:
                # Description is not JSON, that's ok
                pass
        
        if needs_fix:
            # Update the entity with corrected fields
            cursor.execute(
                'UPDATE entities SET attributes = ?, description = ? WHERE id = ?',
                (json.dumps(attr_json), desc_str, entity_id)
            )
            logger.info(f"Fixed entity {entity_id}: moved JSON from description to attributes")
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    except Exception as e:
        logger.error(f"Error fixing entity {entity_id}: {e}")
        conn.rollback()
        conn.close()
        return False

def main():
    """Main function to ensure all entities have correct attributes."""
    logger.info("Starting final entity cleanup")
    
    columns, entities = get_all_entities()
    
    # Get index positions for relevant columns
    try:
        id_idx = columns.index('id')
        name_idx = columns.index('name')
        attr_idx = columns.index('attributes')
        desc_idx = columns.index('description')
    except ValueError as e:
        logger.error(f"Error finding column index: {e}")
        return
    
    logger.info(f"Found {len(entities)} entities to check")
    fixed_count = 0
    
    for entity in entities:
        entity_id = entity[id_idx]
        entity_name = entity[name_idx]
        attributes = entity[attr_idx]
        description = entity[desc_idx]
        
        logger.info(f"Checking entity '{entity_name}' ({entity_id})")
        logger.info(f"  Attributes: {attributes}")
        logger.info(f"  Description: {description}")
        
        if fix_entity(entity_id, attributes, description):
            fixed_count += 1
    
    logger.info(f"Final cleanup complete. Fixed {fixed_count} out of {len(entities)} entities")

if __name__ == "__main__":
    main() 