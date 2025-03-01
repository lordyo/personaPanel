"""
Database storage module for the Entity Simulation Framework.

This module provides functions for interacting with the SQLite database
to store and retrieve entity types, entities, and simulation results.
"""

import sqlite3
import json
import uuid
import os
from typing import Dict, List, Any, Optional, Tuple
import datetime

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'entity_sim.db')


def init_db():
    """
    Initialize the database with the required tables.
    
    Creates the database file and tables if they don't already exist.
    """
    # Create the data directory if it doesn't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create entity_types table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entity_types (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        dimensions TEXT NOT NULL  -- JSON string
    )
    ''')
    
    # Create entities table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entities (
        id TEXT PRIMARY KEY,
        entity_type_id TEXT NOT NULL,
        name TEXT NOT NULL,
        attributes TEXT NOT NULL,  -- JSON string
        FOREIGN KEY (entity_type_id) REFERENCES entity_types (id)
    )
    ''')
    
    # Create contexts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contexts (
        id TEXT PRIMARY KEY,
        description TEXT NOT NULL,
        metadata TEXT  -- JSON string
    )
    ''')
    
    # Create simulations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS simulations (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        context_id TEXT NOT NULL,
        interaction_type TEXT NOT NULL,
        entity_ids TEXT NOT NULL,  -- JSON array of entity IDs
        content TEXT NOT NULL,
        metadata TEXT,  -- JSON string
        FOREIGN KEY (context_id) REFERENCES contexts (id)
    )
    ''')
    
    conn.commit()
    conn.close()


# Entity Type Functions

def save_entity_type(name: str, description: str, dimensions: List[Dict[str, Any]]) -> str:
    """
    Save an entity type to the database.
    
    Args:
        name: Name of the entity type
        description: Description of the entity type
        dimensions: List of dimension dictionaries
        
    Returns:
        ID of the saved entity type
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    entity_type_id = str(uuid.uuid4())
    cursor.execute(
        'INSERT INTO entity_types VALUES (?, ?, ?, ?)',
        (entity_type_id, name, description, json.dumps(dimensions))
    )
    
    conn.commit()
    conn.close()
    return entity_type_id


def get_entity_type(entity_type_id: str) -> Optional[Dict[str, Any]]:
    """
    Get an entity type by ID.
    
    Args:
        entity_type_id: ID of the entity type to retrieve
        
    Returns:
        Entity type dictionary or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM entity_types WHERE id = ?', (entity_type_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row is None:
        return None
    
    return {
        'id': row[0],
        'name': row[1],
        'description': row[2],
        'dimensions': json.loads(row[3])
    }


def get_all_entity_types() -> List[Dict[str, Any]]:
    """
    Get all entity types.
    
    Returns:
        List of entity type dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM entity_types')
    rows = cursor.fetchall()
    
    conn.close()
    
    entity_types = []
    for row in rows:
        entity_types.append({
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'dimensions': json.loads(row[3])
        })
    
    return entity_types


# Entity Functions

def save_entity(entity_type_id: str, name: str, attributes: Dict[str, Any]) -> str:
    """
    Save an entity instance to the database.
    
    Args:
        entity_type_id: ID of the entity type
        name: Name of the entity
        attributes: Dictionary of attribute values
        
    Returns:
        ID of the saved entity
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    entity_id = str(uuid.uuid4())
    cursor.execute(
        'INSERT INTO entities VALUES (?, ?, ?, ?)',
        (entity_id, entity_type_id, name, json.dumps(attributes))
    )
    
    conn.commit()
    conn.close()
    return entity_id


def get_entity(entity_id: str) -> Optional[Dict[str, Any]]:
    """
    Get an entity by ID.
    
    Args:
        entity_id: ID of the entity to retrieve
        
    Returns:
        Entity dictionary or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM entities WHERE id = ?', (entity_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row is None:
        return None
    
    return {
        'id': row[0],
        'entity_type_id': row[1],
        'name': row[2],
        'attributes': json.loads(row[3])
    }


def get_entities_by_type(entity_type_id: str) -> List[Dict[str, Any]]:
    """
    Get all entities of a specific type.
    
    Args:
        entity_type_id: ID of the entity type
        
    Returns:
        List of entity dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM entities WHERE entity_type_id = ?', (entity_type_id,))
    rows = cursor.fetchall()
    
    conn.close()
    
    entities = []
    for row in rows:
        entities.append({
            'id': row[0],
            'entity_type_id': row[1],
            'name': row[2],
            'attributes': json.loads(row[3])
        })
    
    return entities


# Context Functions

def save_context(description: str, metadata: Optional[Dict[str, Any]] = None) -> str:
    """
    Save a context to the database.
    
    Args:
        description: Description of the context
        metadata: Optional metadata dictionary
        
    Returns:
        ID of the saved context
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    context_id = str(uuid.uuid4())
    cursor.execute(
        'INSERT INTO contexts VALUES (?, ?, ?)',
        (context_id, description, json.dumps(metadata) if metadata else None)
    )
    
    conn.commit()
    conn.close()
    return context_id


def get_context(context_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a context by ID.
    
    Args:
        context_id: ID of the context to retrieve
        
    Returns:
        Context dictionary or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM contexts WHERE id = ?', (context_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row is None:
        return None
    
    return {
        'id': row[0],
        'description': row[1],
        'metadata': json.loads(row[2]) if row[2] else None
    }


# Simulation Functions

def save_simulation(
    context_id: str,
    interaction_type: str,
    entity_ids: List[str],
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Save a simulation result to the database.
    
    Args:
        context_id: ID of the context
        interaction_type: Type of interaction (solo, dyadic, group)
        entity_ids: List of entity IDs that participated
        content: Generated content from the simulation
        metadata: Optional metadata dictionary
        
    Returns:
        ID of the saved simulation
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    simulation_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()
    
    cursor.execute(
        'INSERT INTO simulations VALUES (?, ?, ?, ?, ?, ?, ?)',
        (
            simulation_id,
            timestamp,
            context_id,
            interaction_type,
            json.dumps(entity_ids),
            content,
            json.dumps(metadata) if metadata else None
        )
    )
    
    conn.commit()
    conn.close()
    return simulation_id


def get_simulation(simulation_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a simulation by ID.
    
    Args:
        simulation_id: ID of the simulation to retrieve
        
    Returns:
        Simulation dictionary or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM simulations WHERE id = ?', (simulation_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row is None:
        return None
    
    return {
        'id': row[0],
        'timestamp': row[1],
        'context_id': row[2],
        'interaction_type': row[3],
        'entity_ids': json.loads(row[4]),
        'content': row[5],
        'metadata': json.loads(row[6]) if row[6] else None
    }


def get_all_simulations() -> List[Dict[str, Any]]:
    """
    Get all simulations.
    
    Returns:
        List of simulation dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM simulations ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    
    conn.close()
    
    simulations = []
    for row in rows:
        simulations.append({
            'id': row[0],
            'timestamp': row[1],
            'context_id': row[2],
            'interaction_type': row[3],
            'entity_ids': json.loads(row[4]),
            'content': row[5],
            'metadata': json.loads(row[6]) if row[6] else None
        })
    
    return simulations 