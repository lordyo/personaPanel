#!/usr/bin/env python3
"""
Database initialization script.

This script initializes the SQLite database with all required tables.
Run this script to ensure all tables are created properly before using the application.
"""

import os
import sys
import logging
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database with all required tables."""
    # Get the database path from backend/storage.py
    import importlib.util
    spec = importlib.util.spec_from_file_location("storage", "backend/storage.py")
    storage = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(storage)
    
    DB_PATH = storage.DB_PATH
    logger.info(f"Using database: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create entity_types table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entity_types (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        dimensions TEXT NOT NULL,  -- JSON array of dimension objects
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    ''')
    
    # Create entities table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entities (
        id TEXT PRIMARY KEY,
        entity_type_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        attributes TEXT NOT NULL,  -- JSON object of attribute values
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (entity_type_id) REFERENCES entity_types (id)
    )
    ''')
    
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
    
    # Create indices for simulations
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_simulations_context_id ON simulations(context_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_simulations_timestamp ON simulations(timestamp)')
    
    # Create indices for simulation batches
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_batch_simulations_batch_id ON batch_simulations(batch_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_batch_simulations_simulation_id ON batch_simulations(simulation_id)')
    
    conn.commit()
    conn.close()
    
    logger.info("Database tables created successfully")

def main():
    """Initialize the database with all required tables."""
    logger.info("Initializing database...")
    
    try:
        init_db()
        logger.info("Database initialization completed successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 