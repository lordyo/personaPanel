#!/usr/bin/env python3

"""
Entity Attribute Fixer

This script identifies and fixes entity attributes that are stored as text strings
instead of JSON in the database. It will:

1. Identify all entities with invalid attribute formats
2. Convert the textual attributes into proper JSON format
3. Update the database with the fixed attributes

Run this script directly to fix the corrupted entity data.
"""

import sqlite3
import json
import os
import sys
import logging
from typing import Dict, List, Any, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('attribute_fixer')

# Get the database path - corrected to match the actual location
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
    
    cursor.execute('SELECT id, entity_type_id, name, description, attributes FROM entities')
    entities = cursor.fetchall()
    
    conn.close()
    return entities

def parse_attribute_text(text: str) -> Dict[str, Any]:
    """
    Parse attribute text into a proper JSON object.
    This handles the specific format of the attributes we've seen in the logs.
    """
    if not text or text.strip() == '':
        return {}
    
    # If it's already valid JSON, return it
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Otherwise, try to parse the text format into a dict
    attributes = {}
    current_key = None
    
    # Handle the format "- Key: Value" that we've seen in the logs
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line starts with "- " indicating a new attribute
        if line.startswith('- '):
            # Extract the key-value pair
            parts = line[2:].split(':', 1)  # Skip the "- " prefix
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                attributes[key] = value
    
    return attributes

def update_entity_attributes(entity_id: str, attributes: Dict[str, Any]) -> bool:
    """Update an entity's attributes in the database."""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'UPDATE entities SET attributes = ? WHERE id = ?',
            (json.dumps(attributes), entity_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating entity {entity_id}: {e}")
        conn.rollback()
        conn.close()
        return False

def check_entity_attribute_format(entity: Tuple) -> bool:
    """
    Check if an entity's attributes are properly formatted as JSON.
    
    Returns:
        True if attributes are valid JSON, False otherwise
    """
    entity_id, entity_type_id, name, description, attributes_str = entity
    
    try:
        json.loads(attributes_str)
        return True
    except json.JSONDecodeError:
        return False

def fix_entity_attributes():
    """Find and fix entities with corrupted attribute formats."""
    entities = get_all_entities()
    
    valid_count = 0
    corrupted_count = 0
    fixed_count = 0
    
    for entity in entities:
        entity_id, entity_type_id, name, description, attributes_str = entity
        
        if check_entity_attribute_format(entity):
            valid_count += 1
            continue
        
        corrupted_count += 1
        logger.info(f"Found corrupted attributes for entity {name} ({entity_id})")
        
        # Parse the corrupted attributes
        fixed_attributes = parse_attribute_text(attributes_str)
        
        # Update the entity with fixed attributes
        if update_entity_attributes(entity_id, fixed_attributes):
            fixed_count += 1
            logger.info(f"Fixed attributes for entity {name} ({entity_id})")
        else:
            logger.error(f"Failed to fix attributes for entity {name} ({entity_id})")
    
    logger.info(f"Entity attribute check complete:")
    logger.info(f"  - {valid_count} entities have valid attributes")
    logger.info(f"  - {corrupted_count} entities had corrupted attributes")
    logger.info(f"  - {fixed_count} entities were fixed")
    
    return corrupted_count, fixed_count

if __name__ == "__main__":
    logger.info("Starting entity attribute fixer...")
    
    if not os.path.exists(DB_PATH):
        logger.error(f"Database file not found at {DB_PATH}")
        sys.exit(1)
    
    corrupted, fixed = fix_entity_attributes()
    
    if corrupted == 0:
        logger.info("All entity attributes are in valid format. No fixes needed.")
    elif fixed == corrupted:
        logger.info("Successfully fixed all corrupted entity attributes!")
    else:
        logger.warning(f"Fixed {fixed} out of {corrupted} corrupted entities.")

    logger.info("Entity attribute fixing complete.") 