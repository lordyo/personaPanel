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
    
    # Create simulation_batches table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS simulation_batches (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        description TEXT,
        context TEXT NOT NULL,
        metadata TEXT,  -- JSON string
        status TEXT NOT NULL DEFAULT 'pending',
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    ''')
    
    # Create batch_simulations table for the many-to-many relationship
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS batch_simulations (
        batch_id TEXT NOT NULL,
        simulation_id TEXT NOT NULL,
        sequence_number INTEGER NOT NULL,
        PRIMARY KEY (batch_id, simulation_id),
        FOREIGN KEY (batch_id) REFERENCES simulation_batches (id) ON DELETE CASCADE,
        FOREIGN KEY (simulation_id) REFERENCES simulations (id) ON DELETE CASCADE
    )
    ''')
    
    # Create indices for simulation batches
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_batch_simulations_batch_id ON batch_simulations(batch_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_batch_simulations_simulation_id ON batch_simulations(simulation_id)')
    
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


def update_entity(entity_id: str, name: str, description: str, attributes: Dict[str, Any]) -> bool:
    """
    Update an entity by ID.
    
    Args:
        entity_id: ID of the entity to update
        name: New name for the entity
        description: New description for the entity
        attributes: New attributes dictionary
        
    Returns:
        True if update was successful, False if entity not found or update failed
    """
    logger = logging.getLogger('app')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if entity exists
        cursor.execute('SELECT id FROM entities WHERE id = ?', (entity_id,))
        if cursor.fetchone() is None:
            logger.warning(f"Attempted to update non-existent entity: {entity_id}")
            conn.close()
            return False
        
        # Update the entity
        cursor.execute('''
        UPDATE entities
        SET name = ?, description = ?, attributes = ?
        WHERE id = ?
        ''', (name, description, json.dumps(attributes), entity_id))
        
        conn.commit()
        logger.info(f"Updated entity: {entity_id}")
        return True
    except Exception as e:
        logger.error(f"Error updating entity {entity_id}: {str(e)}")
        logger.exception("Entity update error:")
        conn.rollback()
        return False
    finally:
        conn.close()


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
    
    # First get the column names to ensure we map data correctly
    cursor.execute('PRAGMA table_info(simulations)')
    columns = {row[1]: idx for idx, row in enumerate(cursor.fetchall())}
    
    logging.info(f"Simulation table columns: {columns}")
    
    cursor.execute('SELECT * FROM simulations ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    
    logging.info(f"Got {len(rows)} simulations")
    if rows:
        logging.info(f"First row has {len(rows[0])} columns")
    
    # Convert rows to dictionaries
    simulations = []
    for row in rows:
        try:
            simulation = {
                'id': row[columns.get('id', 0)],
                'timestamp': row[columns.get('timestamp', 1)],
                'context_id': row[columns.get('context_id', 2)],
                'interaction_type': row[columns.get('interaction_type', 3)],
            }
            
            # Handle entity_ids
            entity_ids_idx = columns.get('entity_ids', 4)
            if entity_ids_idx < len(row) and row[entity_ids_idx]:
                try:
                    simulation['entity_ids'] = json.loads(row[entity_ids_idx])
                except json.JSONDecodeError:
                    logging.error(f"Failed to parse entity_ids JSON: {row[entity_ids_idx]}")
                    simulation['entity_ids'] = []
            else:
                simulation['entity_ids'] = []
            
            # Handle content
            content_idx = columns.get('content', 5)
            if content_idx < len(row):
                simulation['content'] = row[content_idx]
            else:
                simulation['content'] = ''
            
            # Handle metadata
            metadata_idx = columns.get('metadata', 6)
            if metadata_idx < len(row) and row[metadata_idx]:
                try:
                    simulation['metadata'] = json.loads(row[metadata_idx])
                except json.JSONDecodeError:
                    logging.error(f"Failed to parse metadata JSON: {row[metadata_idx]}")
                    simulation['metadata'] = {}
            else:
                simulation['metadata'] = {}
            
            # Handle name if it exists
            if 'name' in columns and columns['name'] < len(row):
                simulation['name'] = row[columns['name']]
            
            # Handle final_turn_number if it exists
            if 'final_turn_number' in columns and columns['final_turn_number'] < len(row):
                try:
                    simulation['final_turn_number'] = int(row[columns['final_turn_number']])
                except (ValueError, TypeError):
                    logging.error(f"Failed to parse final_turn_number: {row[columns['final_turn_number']]}")
                    simulation['final_turn_number'] = 0
            else:
                simulation['final_turn_number'] = 0
            
            simulations.append(simulation)
        except Exception as e:
            logging.error(f"Error processing simulation row: {str(e)}")
            logging.exception("Exception details:")
    
    conn.close()
    return simulations


def delete_entity(entity_id: str) -> bool:
    """
    Delete an entity by ID.
    
    Args:
        entity_id: The ID of the entity to delete
        
    Returns:
        True if the entity was deleted, False if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if entity exists
        cursor.execute('SELECT id FROM entities WHERE id = ?', (entity_id,))
        if cursor.fetchone() is None:
            logger = logging.getLogger('app')
            logger.warning(f"Attempted to delete non-existent entity: {entity_id}")
            conn.close()
            return False
        
        # Delete the entity from the database
        cursor.execute('DELETE FROM entities WHERE id = ?', (entity_id,))
        conn.commit()
        
        logger = logging.getLogger('app')
        logger.info(f"Deleted entity: {entity_id}")
        return True
    except Exception as e:
        logger = logging.getLogger('app')
        logger.error(f"Error deleting entity {entity_id}: {str(e)}")
        logger.exception("Entity deletion error:")
        conn.rollback()
        return False
    finally:
        conn.close()


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
    
    # Get table columns dynamically
    cursor.execute("PRAGMA table_info(simulations)")
    columns = {row[1]: idx for idx, row in enumerate(cursor.fetchall())}
    
    logging.info(f"Simulation table columns: {columns}")
    
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
    try:
        logging.info(f"Executing query: {query} with params: {params}")
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        logging.info(f"Got {len(rows)} simulations")
        if rows:
            logging.info(f"First row has {len(rows[0])} columns")
        
        # Convert rows to dictionaries
        simulations = []
        for row in rows:
            simulation = {
                'id': row[columns.get('id', 0)],
                'timestamp': row[columns.get('timestamp', 1)],
                'context_id': row[columns.get('context_id', 2)],
                'interaction_type': row[columns.get('interaction_type', 3)],
                'entity_ids': json.loads(row[columns.get('entity_ids', 4)]) if row[columns.get('entity_ids', 4)] else [],
                'content': row[columns.get('content', 5)] if len(row) > columns.get('content', 5) else '',
            }
            
            # Handle optional columns
            if 'metadata' in columns and len(row) > columns['metadata']:
                metadata_str = row[columns['metadata']]
                try:
                    simulation['metadata'] = json.loads(metadata_str) if metadata_str else {}
                except json.JSONDecodeError:
                    logging.error(f"Failed to parse metadata JSON: {metadata_str}")
                    simulation['metadata'] = {}
            else:
                simulation['metadata'] = {}
                
            if 'name' in columns and len(row) > columns['name']:
                simulation['name'] = row[columns['name']]
                
            if 'final_turn_number' in columns and len(row) > columns['final_turn_number']:
                try:
                    simulation['final_turn_number'] = int(row[columns['final_turn_number']])
                except (ValueError, TypeError):
                    logging.error(f"Failed to parse final_turn_number: {row[columns['final_turn_number']]}")
                    simulation['final_turn_number'] = 0
            else:
                simulation['final_turn_number'] = 0
                
            simulations.append(simulation)
            
        return simulations
    except Exception as e:
        logging.error(f"Error fetching simulations: {str(e)}")
        return []
    finally:
        conn.close()


def delete_entity_type(entity_type_id: str) -> bool:
    """
    Delete an entity type from the database.
    
    Args:
        entity_type_id: ID of the entity type to delete
        
    Returns:
        True if deletion was successful, False otherwise
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # First, delete all entities of this type
        cursor.execute('DELETE FROM entities WHERE entity_type_id = ?', (entity_type_id,))
        
        # Then delete the entity type
        cursor.execute('DELETE FROM entity_types WHERE id = ?', (entity_type_id,))
        
        if cursor.rowcount == 0:
            # No rows affected, entity type not found
            conn.rollback()
            conn.close()
            return False
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting entity type: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# Batch Simulation Functions

def create_simulation_batch(
    name: str,
    description: Optional[str],
    context: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a new simulation batch.
    
    Args:
        name: Name of the batch
        description: Optional description of the batch
        context: The context used for all simulations in this batch
        metadata: Optional metadata dictionary
        
    Returns:
        ID of the created batch
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    batch_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()
    
    cursor.execute(
        'INSERT INTO simulation_batches VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (
            batch_id,
            name,
            timestamp,
            description,
            context,
            json.dumps(metadata) if metadata else None,
            'pending',  # Initial status
            datetime.datetime.now().isoformat()
        )
    )
    
    conn.commit()
    conn.close()
    return batch_id

def add_simulation_to_batch(batch_id: str, simulation_id: str, sequence_number: int) -> bool:
    """
    Add a simulation to a batch.
    
    Args:
        batch_id: ID of the batch
        simulation_id: ID of the simulation to add
        sequence_number: Sequence number for ordering simulations in the batch
        
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO batch_simulations VALUES (?, ?, ?)',
            (batch_id, simulation_id, sequence_number)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger = logging.getLogger('app')
        logger.error(f"Error adding simulation {simulation_id} to batch {batch_id}: {str(e)}")
        return False
    finally:
        conn.close()

def update_batch_status(batch_id: str, status: str) -> bool:
    """
    Update the status of a simulation batch.
    
    Args:
        batch_id: ID of the batch
        status: New status ('pending', 'in_progress', 'completed', 'failed')
        
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'UPDATE simulation_batches SET status = ? WHERE id = ?',
            (status, batch_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        logger = logging.getLogger('app')
        logger.error(f"Error updating batch {batch_id} status: {str(e)}")
        return False
    finally:
        conn.close()

def get_simulation_batch(batch_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a simulation batch by ID.
    
    Args:
        batch_id: ID of the batch to retrieve
        
    Returns:
        Batch dictionary or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get the batch
    cursor.execute('SELECT * FROM simulation_batches WHERE id = ?', (batch_id,))
    batch_row = cursor.fetchone()
    
    if not batch_row:
        conn.close()
        return None
    
    # Get all simulations in the batch
    cursor.execute('''
        SELECT s.*, bs.sequence_number 
        FROM simulations s
        JOIN batch_simulations bs ON s.id = bs.simulation_id
        WHERE bs.batch_id = ?
        ORDER BY bs.sequence_number
    ''', (batch_id,))
    
    simulation_rows = cursor.fetchall()
    
    conn.close()
    
    # Get column names for both tables
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('PRAGMA table_info(simulation_batches)')
    batch_columns = [col[1] for col in cursor.fetchall()]
    
    cursor.execute('PRAGMA table_info(simulations)')
    simulation_columns = [col[1] for col in cursor.fetchall()]
    
    conn.close()
    
    # Create batch dictionary
    batch = {}
    for i, column in enumerate(batch_columns):
        if column == 'metadata':
            batch[column] = json.loads(batch_row[i]) if batch_row[i] else None
        else:
            batch[column] = batch_row[i]
    
    # Create simulations list
    simulations = []
    for row in simulation_rows:
        simulation = {}
        for i, column in enumerate(simulation_columns):
            if i < len(row) - 1:  # Exclude the last column which is sequence_number
                if column == 'entity_ids':
                    simulation[column] = json.loads(row[i]) if row[i] else []
                elif column == 'metadata':
                    simulation[column] = json.loads(row[i]) if row[i] else None
                else:
                    simulation[column] = row[i]
        
        # Add sequence number
        simulation['sequence_number'] = row[-1]
        simulations.append(simulation)
    
    batch['simulations'] = simulations
    
    return batch

def get_all_simulation_batches(include_simulations: bool = False) -> List[Dict[str, Any]]:
    """
    Get all simulation batches.
    
    Args:
        include_simulations: Whether to include the simulations in each batch
        
    Returns:
        List of batch dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM simulation_batches ORDER BY timestamp DESC')
    batch_rows = cursor.fetchall()
    
    # Get column names
    cursor.execute('PRAGMA table_info(simulation_batches)')
    batch_columns = [col[1] for col in cursor.fetchall()]
    
    if include_simulations:
        cursor.execute('PRAGMA table_info(simulations)')
        simulation_columns = [col[1] for col in cursor.fetchall()]
    
    batches = []
    for batch_row in batch_rows:
        # Create batch dictionary
        batch = {}
        for i, column in enumerate(batch_columns):
            if column == 'metadata':
                batch[column] = json.loads(batch_row[i]) if batch_row[i] else None
            else:
                batch[column] = batch_row[i]
        
        if include_simulations:
            # Get all simulations in the batch
            cursor.execute('''
                SELECT s.*, bs.sequence_number 
                FROM simulations s
                JOIN batch_simulations bs ON s.id = bs.simulation_id
                WHERE bs.batch_id = ?
                ORDER BY bs.sequence_number
            ''', (batch[batch_columns[0]],))  # Use first column as ID
            
            simulation_rows = cursor.fetchall()
            
            # Create simulations list
            simulations = []
            for row in simulation_rows:
                simulation = {}
                for i, column in enumerate(simulation_columns):
                    if i < len(row) - 1:  # Exclude the last column which is sequence_number
                        if column == 'entity_ids':
                            simulation[column] = json.loads(row[i]) if row[i] else []
                        elif column == 'metadata':
                            simulation[column] = json.loads(row[i]) if row[i] else None
                        else:
                            simulation[column] = row[i]
                
                # Add sequence number
                simulation['sequence_number'] = row[-1]
                simulations.append(simulation)
            
            batch['simulations'] = simulations
        
        batches.append(batch)
    
    conn.close()
    
    return batches

def delete_simulation_batch(batch_id: str) -> bool:
    """
    Delete a simulation batch and all its associated simulations.
    
    Args:
        batch_id: The ID of the batch to delete
        
    Returns:
        True if the batch was deleted, False if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Start a transaction
        conn.execute('BEGIN TRANSACTION')
        
        # Check if batch exists
        cursor.execute('SELECT id FROM simulation_batches WHERE id = ?', (batch_id,))
        if cursor.fetchone() is None:
            conn.rollback()
            return False
        
        # Get all simulation IDs in the batch
        cursor.execute('SELECT simulation_id FROM batch_simulations WHERE batch_id = ?', (batch_id,))
        simulation_ids = [row[0] for row in cursor.fetchall()]
        
        # Delete all associated simulations
        for sim_id in simulation_ids:
            cursor.execute('DELETE FROM simulations WHERE id = ?', (sim_id,))
        
        # Delete all batch-simulation associations
        cursor.execute('DELETE FROM batch_simulations WHERE batch_id = ?', (batch_id,))
        
        # Delete the batch
        cursor.execute('DELETE FROM simulation_batches WHERE id = ?', (batch_id,))
        
        # Commit the transaction
        conn.commit()
        return True
    except Exception as e:
        # Rollback on error
        conn.rollback()
        logger = logging.getLogger('app')
        logger.error(f"Error deleting batch {batch_id}: {str(e)}")
        return False
    finally:
        conn.close() 