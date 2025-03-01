"""
Database mocking utilities for testing.

This module provides functions to patch the database connection in the storage module
to use an in-memory SQLite database for testing.
"""

import sqlite3
import json
import uuid
import sys
import traceback
from typing import Dict, List, Any, Optional, Callable
from unittest.mock import patch, MagicMock
from backend import storage

# Debug mode for tracing issues
DEBUG_MODE = True

def log_debug(message):
    """Print debug message if DEBUG_MODE is enabled."""
    if DEBUG_MODE:
        print(f"DB_MOCK DEBUG: {message}")

# Store the original sqlite3.connect function
original_sqlite3_connect = sqlite3.connect
# Store the original init_db function
original_init_db = storage.init_db
# Store the original save_entity_type function
original_save_entity_type = storage.save_entity_type
# Store the original get_entity_type function
original_get_entity_type = storage.get_entity_type

# Global variable to hold the in-memory database connection
_test_conn = None

def create_in_memory_db():
    """Create an in-memory SQLite database for testing."""
    global _test_conn
    
    log_debug("Creating in-memory database")
    
    # Create a connection to an in-memory database
    if _test_conn is None or not is_connection_valid(_test_conn):
        # Always use the original connect method to avoid recursion
        _test_conn = original_sqlite3_connect(':memory:', check_same_thread=False)
        
        # Initialize the database with the schema
        cursor = _test_conn.cursor()
        
        # Create the entity_types table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS entity_types (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            dimensions TEXT NOT NULL
        )
        ''')
        
        # Create the entity_type_dimensions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS entity_type_dimensions (
            id TEXT PRIMARY KEY,
            entity_type_id TEXT,
            name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            options TEXT,
            min_value REAL,
            max_value REAL,
            distribution TEXT,
            FOREIGN KEY (entity_type_id) REFERENCES entity_types (id)
        )
        ''')
        
        # Create the entities table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS entities (
            id TEXT PRIMARY KEY,
            entity_type_id TEXT,
            name TEXT NOT NULL,
            attributes TEXT NOT NULL,
            FOREIGN KEY (entity_type_id) REFERENCES entity_types (id)
        )
        ''')
        
        # Create the entity_attributes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS entity_attributes (
            id TEXT PRIMARY KEY,
            entity_id TEXT,
            name TEXT NOT NULL,
            value TEXT,
            FOREIGN KEY (entity_id) REFERENCES entities (id)
        )
        ''')
        
        # Create the contexts table (renamed from simulation_contexts to match the schema in storage.py)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS contexts (
            id TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            metadata TEXT
        )
        ''')
        
        # Create the simulations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS simulations (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            context_id TEXT NOT NULL,
            interaction_type TEXT NOT NULL,
            entity_ids TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT,
            FOREIGN KEY (context_id) REFERENCES contexts (id)
        )
        ''')
        
        # Commit the changes
        _test_conn.commit()
        log_debug("In-memory database created successfully")
        
    return _test_conn

def is_connection_valid(conn):
    """Check if a connection is still valid and open."""
    if conn is None:
        return False
    
    try:
        conn.execute("SELECT 1")
        return True
    except sqlite3.ProgrammingError:
        log_debug("Connection is closed")
        return False
    except Exception as e:
        log_debug(f"Connection check error: {e}")
        return False

def get_test_connection():
    """Get the test database connection."""
    global _test_conn
    if _test_conn is None or not is_connection_valid(_test_conn):
        create_in_memory_db()
    return _test_conn

def close_test_connection():
    """Close the global test connection."""
    global _test_conn
    if _test_conn is not None:
        log_debug("Closing test connection")
        try:
            _test_conn.close()
        except Exception as e:
            log_debug(f"Error closing connection: {e}")
        _test_conn = None

# Mock for save_entity_type to handle dimension conversion
def mock_save_entity_type(name, description, dimensions):
    """Mock for storage.save_entity_type that handles dimension conversion."""
    log_debug(f"Mock save_entity_type called with name={name}, dimensions={len(dimensions)}")
    
    # Generate a UUID for the entity type
    entity_type_id = str(uuid.uuid4())
    
    try:
        # Connect to the in-memory database
        conn = get_test_connection()
        cursor = conn.cursor()
        
        # Save the entity type
        cursor.execute(
            'INSERT INTO entity_types VALUES (?, ?, ?, ?)',
            (entity_type_id, name, description, json.dumps(dimensions))
        )
        
        conn.commit()
        log_debug(f"Entity type saved with ID: {entity_type_id}")
        return entity_type_id
    except Exception as e:
        log_debug(f"Error in mock_save_entity_type: {e}")
        traceback.print_exc(file=sys.stdout)
        raise

# This function will be our replacement for sqlite3.connect
def mock_sqlite3_connect(*args, **kwargs):
    """Mock for sqlite3.connect to return our test connection."""
    log_debug(f"Mock connect called with args: {args}, kwargs: {kwargs}")
    
    # For in-memory or patched DB_PATH, return our test connection
    if args and (args[0] == ':memory:' or args[0] == storage.DB_PATH):
        conn = get_test_connection()
        log_debug("Returning test connection")
        return conn
    
    # For all other connections, use the original connect function
    log_debug(f"Using original connect for: {args}")
    return original_sqlite3_connect(*args, **kwargs)

# Mock the init_db function to avoid file system operations
def mock_init_db():
    """Mock for storage.init_db that skips file system operations."""
    log_debug("Mock init_db called")
    
    # Simply create and return the in-memory database
    get_test_connection()
    
    log_debug("Mock init_db completed")

# Mock for get_entity_type to handle nonexistent entity types
def mock_get_entity_type(entity_type_id):
    """Mock for storage.get_entity_type that handles nonexistent entities."""
    log_debug(f"Mock get_entity_type called with id={entity_type_id}")
    
    try:
        # Connect to the in-memory database
        conn = get_test_connection()
        cursor = conn.cursor()
        
        # Query the entity type
        cursor.execute('SELECT * FROM entity_types WHERE id = ?', (entity_type_id,))
        entity_type = cursor.fetchone()
        
        if entity_type is None:
            log_debug(f"Entity type not found: {entity_type_id}")
            return None
        
        # Parse the entity type
        id, name, description, dimensions_json = entity_type
        dimensions = json.loads(dimensions_json)
        
        entity_type_dict = {
            'id': id,
            'name': name,
            'description': description,
            'dimensions': dimensions
        }
        
        log_debug(f"Entity type found: {id}")
        return entity_type_dict
    except Exception as e:
        log_debug(f"Error in mock_get_entity_type: {e}")
        traceback.print_exc(file=sys.stdout)
        raise

def apply_db_patches():
    """Apply patches to the storage module to use our in-memory database."""
    log_debug("Applying patches to storage module")
    
    # Patch sqlite3.connect to use our mock function
    sqlite3.connect = mock_sqlite3_connect
    
    # Patch the init_db function to avoid file system operations
    storage.init_db = mock_init_db
    
    # Patch the save_entity_type function to handle dimension conversion
    storage.save_entity_type = mock_save_entity_type
    
    # Patch the get_entity_type function to handle nonexistent entities
    storage.get_entity_type = mock_get_entity_type
    
    # Set the DB_PATH to use in-memory database
    original_db_path = storage.DB_PATH
    storage.DB_PATH = ':memory:'
    
    # Initialize the test database
    get_test_connection()
    
    log_debug("Database patches applied successfully")
    
    return original_db_path

def restore_db_patches(original_db_path):
    """Restore the original database connection and path."""
    log_debug("Restoring original database connection")
    
    # Restore the original connect function
    sqlite3.connect = original_sqlite3_connect
    
    # Restore the original init_db function
    storage.init_db = original_init_db
    
    # Restore the original save_entity_type function
    storage.save_entity_type = original_save_entity_type
    
    # Restore the original get_entity_type function
    storage.get_entity_type = original_get_entity_type
    
    # Restore the original DB_PATH
    storage.DB_PATH = original_db_path
    
    # Close the test connection
    close_test_connection()
    
    log_debug("Original database connection restored") 