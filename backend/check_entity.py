#!/usr/bin/env python3

"""
Entity Database Check

This script checks the actual values of entities in the database
to diagnose potential issues with field ordering or data formats.
"""

import sqlite3
import json
import os
import sys

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'entity_sim.db')

def check_entity(entity_id):
    """Check the field values for a specific entity."""
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get column names
    cursor.execute("PRAGMA table_info(entities)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Entity table columns: {columns}")
    
    # Get entity data
    cursor.execute(f"SELECT * FROM entities WHERE id = ?", (entity_id,))
    entity_data = cursor.fetchone()
    
    if not entity_data:
        print(f"No entity found with ID: {entity_id}")
        return
    
    # Print all fields
    print("\nEntity data:")
    for i, col in enumerate(columns):
        print(f"{col}: {entity_data[i]}")
        
        # For JSON fields, try to parse and pretty print
        if col in ['attributes', 'description'] and entity_data[i]:
            try:
                parsed = json.loads(entity_data[i])
                print(f"  Parsed {col}: {json.dumps(parsed, indent=2)}")
            except json.JSONDecodeError:
                print(f"  {col} is not valid JSON")
    
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_entity.py <entity_id>")
        sys.exit(1)
    
    entity_id = sys.argv[1]
    check_entity(entity_id) 