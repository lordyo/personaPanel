#!/usr/bin/env python3
"""
Database initialization script for the Entity Simulation Framework.

This script initializes the SQLite database and optionally populates it
with default entity types.
"""

import os
import sys
import json

# Add the parent directory to the path so we can import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import backend.storage as storage
from backend.core.entity import Dimension, EntityType


def init_db():
    """Initialize the database and create tables."""
    print("Initializing database...")
    storage.init_db()
    print("Database initialized successfully!")


def load_default_entity_types():
    """Load default entity types from JSON."""
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
    default_entities_path = os.path.join(config_dir, 'default_entities.json')
    
    if not os.path.exists(default_entities_path):
        print(f"Default entities file not found at {default_entities_path}")
        return
    
    try:
        with open(default_entities_path, 'r') as f:
            default_entities = json.load(f)
        
        for entity_type in default_entities:
            name = entity_type['name']
            description = entity_type['description']
            dimensions = entity_type['dimensions']
            
            # Check if entity type already exists
            existing = False
            entity_types = storage.get_all_entity_types()
            for et in entity_types:
                if et['name'] == name:
                    existing = True
                    break
            
            if not existing:
                entity_type_id = storage.save_entity_type(name, description, dimensions)
                print(f"Added default entity type: {name} (ID: {entity_type_id})")
            else:
                print(f"Entity type {name} already exists, skipping")
                
        print("Default entity types loaded successfully!")
        
    except Exception as e:
        print(f"Error loading default entity types: {e}")


if __name__ == '__main__':
    init_db()
    
    # Check if the default_entities.json file exists
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
    default_entities_path = os.path.join(config_dir, 'default_entities.json')
    
    if os.path.exists(default_entities_path):
        load_default_entity_types()
    else:
        print("No default entity types found. Creating only the database structure.")
        print(f"You can add default entity types by creating a file at: {default_entities_path}") 