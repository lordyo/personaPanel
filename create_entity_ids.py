#!/usr/bin/env python3
"""
Script to create an entity_ids.json file with real entity IDs from the database.

This script helps you create a JSON file containing entity IDs for use with
batch simulations. It fetches entity types and entities from the database
and lets you select which ones to include.
"""

import os
import sys
import json
import sqlite3

# Add the backend directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the storage module
from backend import storage

def get_db_path():
    """Get the database path from the storage module."""
    return storage.DB_PATH

def get_all_entity_types():
    """Get all entity types from the database."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM entity_types')
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute('PRAGMA table_info(entity_types)')
    columns = [col[1] for col in cursor.fetchall()]
    
    entity_types = []
    for row in rows:
        entity_type = {}
        for i, column in enumerate(columns):
            if column == 'dimensions':
                entity_type[column] = json.loads(row[i]) if row[i] else []
            else:
                entity_type[column] = row[i]
        entity_types.append(entity_type)
    
    conn.close()
    return entity_types

def get_entities_by_type(entity_type_id):
    """Get all entities of a specific type."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM entities WHERE entity_type_id = ?', (entity_type_id,))
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute('PRAGMA table_info(entities)')
    columns = [col[1] for col in cursor.fetchall()]
    
    entities = []
    for row in rows:
        entity = {}
        for i, column in enumerate(columns):
            if column == 'attributes':
                entity[column] = json.loads(row[i]) if row[i] else {}
            else:
                entity[column] = row[i]
        entities.append(entity)
    
    conn.close()
    return entities

def main():
    """Create an entity_ids.json file with real entity IDs."""
    print("Fetching entity types from database...")
    
    try:
        # First, initialize the database to ensure tables exist
        from initialize_db import init_db
        init_db()
        
        # Then get entity types
        entity_types = get_all_entity_types()
        
        if not entity_types:
            print("No entity types found in database.")
            create_dummy_entities()
            return
        
        print(f"Found {len(entity_types)} entity type(s):")
        for i, entity_type in enumerate(entity_types):
            print(f"{i+1}. {entity_type['name']} (ID: {entity_type['id']})")
        
        choice = input("\nSelect entity type number to use (or 'all' for all types): ")
        
        entity_ids = []
        
        if choice.lower() == 'all':
            # Get entities from all types
            for entity_type in entity_types:
                entities = get_entities_by_type(entity_type['id'])
                if entities:
                    new_ids = [entity['id'] for entity in entities]
                    print(f"Found {len(new_ids)} entities for type {entity_type['name']}")
                    entity_ids.extend(new_ids)
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(entity_types):
                    entity_type = entity_types[index]
                    entities = get_entities_by_type(entity_type['id'])
                    if entities:
                        entity_ids = [entity['id'] for entity in entities]
                        print(f"Found {len(entity_ids)} entities for type {entity_type['name']}")
                    else:
                        print(f"No entities found for type {entity_type['name']}")
                else:
                    print(f"Invalid selection. Please choose a number between 1 and {len(entity_types)}.")
                    create_dummy_entities()
                    return
            except ValueError:
                print("Invalid input. Please enter a number or 'all'.")
                create_dummy_entities()
                return
        
        if not entity_ids:
            print("No entity IDs found. Creating dummy entity IDs instead.")
            create_dummy_entities()
            return
        
        # Limit the number of entities if needed
        max_entities = input(f"\nFound {len(entity_ids)} total entities. How many to include? (default: all): ")
        if max_entities.strip():
            try:
                max_entities = int(max_entities)
                entity_ids = entity_ids[:max_entities]
            except ValueError:
                print("Invalid input. Using all entities.")
        
        # Save to file
        filename = input("\nEnter filename to save entity IDs (default: entity_ids.json): ")
        if not filename.strip():
            filename = "entity_ids.json"
        
        with open(filename, 'w') as f:
            json.dump(entity_ids, f)
        
        print(f"Saved {len(entity_ids)} entity IDs to {filename}")
        return filename
        
    except Exception as e:
        print(f"Error fetching entity types: {str(e)}")
        print("Creating dummy entity IDs instead.")
        create_dummy_entities()
        return

def create_dummy_entities():
    """Create a file with dummy entity IDs for testing."""
    import uuid
    
    # Create dummy entity IDs
    entity_ids = [str(uuid.uuid4()) for _ in range(5)]
    
    # Save to file
    filename = input("\nEnter filename to save dummy entity IDs (default: entity_ids.json): ")
    if not filename.strip():
        filename = "entity_ids.json"
    
    with open(filename, 'w') as f:
        json.dump(entity_ids, f)
    
    print(f"Created {len(entity_ids)} dummy entity IDs in {filename}")
    return filename

if __name__ == "__main__":
    main() 