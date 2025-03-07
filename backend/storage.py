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
import logging

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
        dimensions TEXT NOT NULL,  -- JSON string
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    ''')
    
    # Create indices for entity_types
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_entity_types_name ON entity_types(name)')
    
    # Create entities table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entities (
        id TEXT PRIMARY KEY,
        entity_type_id TEXT NOT NULL,
        name TEXT NOT NULL,
        attributes TEXT NOT NULL,  -- JSON string
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        description TEXT NOT NULL,
        FOREIGN KEY (entity_type_id) REFERENCES entity_types (id)
    )
    ''')
    
    # Create indices for entities
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_entity_type_id ON entities(entity_type_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name)')
    
    # Create contexts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contexts (
        id TEXT PRIMARY KEY,
        description TEXT NOT NULL,
        metadata TEXT,  -- JSON string
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
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
        final_turn_number INTEGER NOT NULL,
        FOREIGN KEY (context_id) REFERENCES contexts (id)
    )
    ''')
    
    # Create indices for simulations
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_simulations_context_id ON simulations(context_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_simulations_timestamp ON simulations(timestamp)')
    
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
        'INSERT INTO entity_types VALUES (?, ?, ?, ?, ?)',
        (entity_type_id, name, description, json.dumps(dimensions), datetime.datetime.now().isoformat())
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
        'dimensions': json.loads(row[3]),
        'created_at': row[4]
    }


def get_all_entity_types() -> List[Dict[str, Any]]:
    """
    Get all entity types from the database.
    
    Returns:
        List of entity type dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, name, description, dimensions, created_at
    FROM entity_types
    ORDER BY name
    ''')
    
    rows = cursor.fetchall()
    entity_types = []
    
    for row in rows:
        entity_type = {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'dimensions': json.loads(row['dimensions']),
            'created_at': row['created_at']
        }
        entity_types.append(entity_type)
    
    conn.close()
    return entity_types


def update_entity_type(entity_type_id: str, name: str, description: str, dimensions: List[Dict[str, Any]]) -> bool:
    """
    Update an existing entity type in the database.
    
    Args:
        entity_type_id: ID of the entity type to update
        name: New name of the entity type
        description: New description of the entity type
        dimensions: New list of dimension objects
        
    Returns:
        True if the update was successful, False otherwise
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        UPDATE entity_types
        SET name = ?, description = ?, dimensions = ?
        WHERE id = ?
        ''', (name, description, json.dumps(dimensions), entity_type_id))
        
        if cursor.rowcount == 0:
            # No rows were updated, entity type not found
            conn.close()
            return False
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating entity type: {e}")
        conn.rollback()
        conn.close()
        return False


# Entity Functions

def save_entity(entity_type_id: str, name: str, description: str, attributes: Dict[str, Any]) -> str:
    """
    Save an entity instance to the database.
    
    Args:
        entity_type_id: ID of the entity type
        name: Name of the entity
        description: Description of the entity
        attributes: Dictionary of attribute values
        
    Returns:
        ID of the saved entity
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    entity_id = str(uuid.uuid4())
    
    # Correct field order to match actual database schema:
    # id, entity_type_id, name, attributes, created_at, description
    cursor.execute(
        'INSERT INTO entities VALUES (?, ?, ?, ?, ?, ?)',
        (
            entity_id, 
            entity_type_id, 
            name, 
            json.dumps(attributes),  # Attributes is 4th column
            datetime.datetime.now().isoformat(),  # created_at is 5th column
            description  # Description is 6th column
        )
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
    logger = logging.getLogger('app')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM entities WHERE id = ?', (entity_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row is None:
        return None
    
    try:
        # The correct column order in the database is:
        # id(0), entity_type_id(1), name(2), attributes(3), created_at(4), description(5)
        attributes = json.loads(row[3])
        return {
            'id': row[0],
            'entity_type_id': row[1],
            'name': row[2],
            'attributes': attributes,
            'created_at': row[4],
            'description': row[5]
        }
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse attributes for entity {entity_id}: {e}")
        # Return entity with empty attributes instead of failing
        return {
            'id': row[0],
            'entity_type_id': row[1],
            'name': row[2],
            'attributes': {},
            'created_at': row[4],
            'description': row[5]
        }


def get_entities_by_type(entity_type_id: str) -> List[Dict[str, Any]]:
    """
    Get all entities of a specific type.
    
    Args:
        entity_type_id: ID of the entity type
        
    Returns:
        List of entity dictionaries
    """
    logger = logging.getLogger('app')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM entities WHERE entity_type_id = ?', (entity_type_id,))
    rows = cursor.fetchall()
    
    conn.close()
    
    entities = []
    for row in rows:
        try:
            # The correct column order in the database is:
            # id(0), entity_type_id(1), name(2), attributes(3), created_at(4), description(5)
            attributes = json.loads(row[3])
            entities.append({
                'id': row[0],
                'entity_type_id': row[1],
                'name': row[2],
                'attributes': attributes,
                'created_at': row[4],
                'description': row[5]
            })
        except json.JSONDecodeError as e:
            # Log the error but skip this entity
            logger.error(f"Failed to parse attributes for entity {row[0]}, skipping: {e}")
            continue
    
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
        'INSERT INTO contexts VALUES (?, ?, ?, ?)',
        (context_id, description, json.dumps(metadata) if metadata else None, datetime.datetime.now().isoformat())
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
        'metadata': json.loads(row[2]) if row[2] else None,
        'created_at': row[3]
    }


# Simulation Functions

def save_simulation(
    context_id: str,
    interaction_type: str,
    entity_ids: List[str],
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    final_turn_number: Optional[int] = 0,
    name: Optional[str] = None
) -> str:
    """
    Save a simulation result to the database.
    
    Args:
        context_id: ID of the context
        interaction_type: Type of interaction (solo, dyadic, group)
        entity_ids: List of entity IDs that participated
        content: Generated content from the simulation
        metadata: Optional metadata dictionary
        final_turn_number: Final turn number for the simulation (default: 0)
        name: Optional name for the simulation
        
    Returns:
        ID of the saved simulation
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get column names to ensure we're providing the right number of values
    cursor.execute('PRAGMA table_info(simulations)')
    columns = [col[1] for col in cursor.fetchall()]
    
    simulation_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()
    
    # Default simulation name if not provided
    if name is None:
        name = f"Simulation {timestamp[:10]}"
    
    # Handle case where table has a name column
    if 'name' in columns:
        cursor.execute(
            'INSERT INTO simulations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                simulation_id,
                timestamp,
                context_id,
                interaction_type,
                json.dumps(entity_ids),
                content,
                json.dumps(metadata) if metadata else None,
                name,
                final_turn_number
            )
        )
    else:
        # Fallback for older schema without name column
        cursor.execute(
            'INSERT INTO simulations VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (
                simulation_id,
                timestamp,
                context_id,
                interaction_type,
                json.dumps(entity_ids),
                content,
                json.dumps(metadata) if metadata else None,
                final_turn_number
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
    
    # First get the column names to ensure we map data correctly
    cursor.execute('PRAGMA table_info(simulations)')
    columns = [col[1] for col in cursor.fetchall()]
    
    cursor.execute('SELECT * FROM simulations WHERE id = ?', (simulation_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row is None:
        return None
    
    # Create a dictionary mapping column names to values
    simulation = {}
    for i, column in enumerate(columns):
        if i < len(row):  # Ensure we don't go out of bounds
            if column == 'entity_ids':
                simulation[column] = json.loads(row[i]) if row[i] else []
            elif column == 'metadata':
                simulation[column] = json.loads(row[i]) if row[i] else None
            elif column == 'final_turn_number':
                try:
                    simulation[column] = int(row[i]) if row[i] is not None else 0
                except (ValueError, TypeError):
                    logger = logging.getLogger('app')
                    logger.warning(f"Invalid final_turn_number value for simulation {simulation_id}: {row[i]}")
                    simulation[column] = 0
            else:
                simulation[column] = row[i]
    
    return simulation


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
            'metadata': json.loads(row[6]) if row[6] else None,
            'final_turn_number': row[7]
        })
    
    return simulations


def delete_entity(entity_id: str) -> bool:
    """
    Delete an entity by ID.
    
    Args:
        entity_id: The ID of the entity to delete
        
    Returns:
        True if the entity was deleted, False if not found
    """
    data_path = os.path.join(os.path.dirname(DB_PATH), 'entities', f"{entity_id}.json")
    
    if not os.path.exists(data_path):
        logger = logging.getLogger('app')
        logger.warning(f"Attempted to delete non-existent entity: {entity_id}")
        return False
    
    try:
        os.remove(data_path)
        logger = logging.getLogger('app')
        logger.info(f"Deleted entity: {entity_id}")
        return True
    except Exception as e:
        logger = logging.getLogger('app')
        logger.error(f"Error deleting entity {entity_id}: {str(e)}")
        logger.exception("Entity deletion error:")
        return False


def delete_simulation(simulation_id: str) -> bool:
    """
    Delete a simulation by ID.
    
    Args:
        simulation_id: The ID of the simulation to delete
        
    Returns:
        True if the simulation was deleted, False if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if simulation exists
        cursor.execute('SELECT id FROM simulations WHERE id = ?', (simulation_id,))
        if cursor.fetchone() is None:
            return False
        
        # Delete the simulation
        cursor.execute('DELETE FROM simulations WHERE id = ?', (simulation_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger = logging.getLogger('app')
        logger.error(f"Error deleting simulation {simulation_id}: {str(e)}")
        logger.exception("Simulation deletion error:")
        conn.rollback()
        return False
    finally:
        conn.close()


def delete_entities_by_type(entity_type_id: str) -> int:
    """
    Delete all entities of a specific entity type.
    
    Args:
        entity_type_id: The ID of the entity type
        
    Returns:
        The number of entities deleted
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Delete all entities of the specified type
        cursor.execute('DELETE FROM entities WHERE entity_type_id = ?', (entity_type_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        return deleted_count
    except Exception as e:
        print(f"Error deleting entities by type: {e}")
        conn.rollback()
        return 0
    finally:
        conn.close()


def update_simulation(
    simulation_id: str,
    content: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    final_turn_number: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Update a simulation with new content, metadata, or final_turn_number.
    
    Args:
        simulation_id: ID of the simulation to update
        content: New content (optional)
        metadata: New metadata to merge (optional)
        final_turn_number: New final turn number (optional)
        
    Returns:
        The updated simulation as a dictionary
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get the column names to ensure we map data correctly
    cursor.execute('PRAGMA table_info(simulations)')
    columns = [col[1] for col in cursor.fetchall()]

    # Check if final_turn_number column exists
    has_final_turn_column = 'final_turn_number' in columns
    
    # Get the current simulation
    cursor.execute('SELECT * FROM simulations WHERE id = ?', (simulation_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    # Create a dictionary mapping column names to values
    current_simulation = {}
    for i, column in enumerate(columns):
        if i < len(row):  # Ensure we don't go out of bounds
            if column == 'entity_ids' or column == 'metadata':
                current_simulation[column] = json.loads(row[i]) if row[i] else {}
            elif column == 'final_turn_number':
                try:
                    current_simulation[column] = int(row[i]) if row[i] is not None else 0
                except (ValueError, TypeError):
                    current_simulation[column] = 0
            else:
                current_simulation[column] = row[i]
    
    # Update metadata if provided, otherwise keep existing
    existing_metadata = current_simulation.get('metadata', {}) or {}
    updated_metadata = {**existing_metadata, **(metadata or {})}
    
    # Update final_turn_number if provided, otherwise keep existing
    new_final_turn_number = final_turn_number
    if final_turn_number is None and has_final_turn_column:
        new_final_turn_number = current_simulation.get('final_turn_number', 0)
    
    # Update content if provided, otherwise keep existing
    new_content = content
    if content is None:
        new_content = current_simulation.get('content', '')
    
    # Update the simulation
    if has_final_turn_column:
        cursor.execute(
            'UPDATE simulations SET content = ?, metadata = ?, final_turn_number = ? WHERE id = ?',
            (new_content, json.dumps(updated_metadata), new_final_turn_number, simulation_id)
        )
    else:
        cursor.execute(
            'UPDATE simulations SET content = ?, metadata = ? WHERE id = ?',
            (new_content, json.dumps(updated_metadata), simulation_id)
        )
    
    conn.commit()
    
    # Fetch the updated simulation
    cursor.execute('SELECT * FROM simulations WHERE id = ?', (simulation_id,))
    updated_row = cursor.fetchone()
    
    conn.close()
    
    if not updated_row:
        return None
    
    # Create a dictionary for the updated simulation
    updated_simulation = {}
    for i, column in enumerate(columns):
        if i < len(updated_row):  # Ensure we don't go out of bounds
            if column == 'entity_ids':
                updated_simulation[column] = json.loads(updated_row[i]) if updated_row[i] else []
            elif column == 'metadata':
                updated_simulation[column] = json.loads(updated_row[i]) if updated_row[i] else None
            elif column == 'final_turn_number':
                try:
                    updated_simulation[column] = int(updated_row[i]) if updated_row[i] is not None else 0
                except (ValueError, TypeError):
                    updated_simulation[column] = 0
            else:
                updated_simulation[column] = updated_row[i]
    
    # Ensure API compatibility with old code
    if 'content' in updated_simulation and 'result' not in updated_simulation:
        updated_simulation['result'] = updated_simulation['content']
    
    return updated_simulation


def get_simulations(
    entity_id: Optional[str] = None,
    entity_type_id: Optional[str] = None,
    interaction_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get a list of simulations with optional filtering.
    
    Args:
        entity_id: Filter by entity ID
        entity_type_id: Filter by entity type ID
        interaction_type: Filter by interaction type (solo, dyadic, group)
        limit: Maximum number of simulations to return
        offset: Number of simulations to skip for pagination
        
    Returns:
        List of simulation dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query_parts = ['SELECT * FROM simulations']
    params = []
    where_clauses = []
    
    # Apply filters
    if interaction_type:
        where_clauses.append('interaction_type = ?')
        params.append(interaction_type)
    
    if entity_id or entity_type_id:
        # We need to join with entities table for these filters
        if entity_id:
            # Filter by entity ID - need to check JSON entity_ids field
            where_clauses.append("entity_ids LIKE ?")
            params.append(f'%"{entity_id}"%')
        
        if entity_type_id:
            # Get all entity IDs of this type
            cursor.execute(
                'SELECT id FROM entities WHERE entity_type_id = ?',
                (entity_type_id,)
            )
            type_entity_ids = [row[0] for row in cursor.fetchall()]
            
            # Build a complex WHERE clause to check if any of these IDs are in the entity_ids JSON
            if type_entity_ids:
                type_where = []
                for type_entity_id in type_entity_ids:
                    type_where.append("entity_ids LIKE ?")
                    params.append(f'%"{type_entity_id}"%')
                
                where_clauses.append(f"({' OR '.join(type_where)})")
    
    # Add WHERE clause if needed
    if where_clauses:
        query_parts.append(f"WHERE {' AND '.join(where_clauses)}")
    
    # Add ORDER BY, LIMIT, and OFFSET
    query_parts.append('ORDER BY timestamp DESC')
    query_parts.append('LIMIT ? OFFSET ?')
    params.append(limit)
    params.append(offset)
    
    # Execute the query
    query = ' '.join(query_parts)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Convert rows to dictionaries
    simulations = []
    for row in rows:
        simulations.append({
            'id': row[0],
            'created_at': row[1],
            'context_id': row[2],
            'interaction_type': row[3],
            'entity_ids': json.loads(row[4]),
            'result': row[5],
            'metadata': json.loads(row[6]) if row[6] else None,
            'final_turn_number': row[7]
        })
    
    conn.close()
    return simulations 