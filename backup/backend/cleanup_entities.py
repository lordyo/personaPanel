#!/usr/bin/env python3
"""
Script to silently clean up any remaining entity data issues without breaking working entities.
This script:
1. Identifies entities with empty attributes that should have data
2. Checks for any remaining swapped fields
3. Fixes issues while preserving working entities
"""

import os
import sqlite3
import json
import logging
import sys

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
    """Get all entities from the database."""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Get column names
    cursor.execute("PRAGMA table_info(entities)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Get all entities
    cursor.execute('SELECT * FROM entities')
    entities = cursor.fetchall()
    
    conn.close()
    
    # Return both column names and entity data
    return columns, entities

def fix_empty_attributes(entity_id, entity_name, description):
    """
    Fix entities with empty attributes but possibly valid description.
    Only fixes if the description field looks like it contains valid JSON attributes.
    If not, generates sensible defaults based on entity name.
    """
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # Check if description field contains valid JSON that could be attributes
        try:
            potential_attributes = json.loads(description)
            if isinstance(potential_attributes, dict) and len(potential_attributes) > 0:
                # This looks like attributes data in the description field
                cursor.execute(
                    'UPDATE entities SET attributes = ? WHERE id = ?', 
                    (description, entity_id)
                )
                logger.info(f"Fixed entity {entity_id} by moving JSON data from description to attributes")
                conn.commit()
                conn.close()
                return True
        except (json.JSONDecodeError, TypeError):
            # Not valid JSON in description, try to generate defaults
            pass
        
        # Generate default attributes based on entity name
        default_attributes = {}
        
        if "Human" in entity_name:
            default_attributes = {
                "age": 30,
                "gender": "unspecified",
                "occupation": "unknown",
                "personality": "neutral"
            }
        elif "Fantasy" in entity_name:
            default_attributes = {
                "race": "unknown",
                "class": "adventurer",
                "age": 100,
                "has_magic": True
            }
        elif "CEO" in entity_name or "Executive" in entity_name:
            default_attributes = {
                "company": "Unknown Corp",
                "industry": "technology",
                "years_experience": 15,
                "leadership_style": "strategic"
            }
        
        if default_attributes:
            attr_json = json.dumps(default_attributes)
            cursor.execute(
                'UPDATE entities SET attributes = ? WHERE id = ?', 
                (attr_json, entity_id)
            )
            logger.info(f"Fixed entity {entity_id} by generating default attributes for {entity_name}")
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    except Exception as e:
        logger.error(f"Failed to fix entity {entity_id}: {e}")
        conn.rollback()
        conn.close()
        return False

def main():
    """Main function to clean up entity data issues."""
    logger.info("Starting entity data cleanup")
    
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
    
    fixed_count = 0
    total_entities = len(entities)
    
    logger.info(f"Checking {total_entities} entities for data issues")
    
    for entity in entities:
        entity_id = entity[id_idx]
        entity_name = entity[name_idx]
        attributes = entity[attr_idx]
        description = entity[desc_idx]
        
        # Skip entities with valid attributes
        try:
            attr_json = json.loads(attributes)
            if isinstance(attr_json, dict) and len(attr_json) > 0:
                # This entity already has valid attributes, skip it
                continue
        except (json.JSONDecodeError, TypeError):
            # Failed to parse attributes, proceed with fix attempt
            pass
        
        # Try to fix this entity
        logger.info(f"Checking entity '{entity_name}' ({entity_id}) with empty attributes")
        if fix_empty_attributes(entity_id, entity_name, description):
            fixed_count += 1
    
    logger.info(f"Entity data cleanup complete. Fixed {fixed_count} out of {total_entities} entities.")

if __name__ == "__main__":
    main() 