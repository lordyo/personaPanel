#!/usr/bin/env python3
"""
Script to view batch simulation results from the database.

This script retrieves and displays batch simulation results, making it easier
to view the outcomes without needing to use the API endpoints.
"""

import os
import sys
import json
import sqlite3
from typing import Dict, List, Any, Optional

# Add the backend directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def get_db_path():
    """Get the database path."""
    from backend import storage
    return storage.DB_PATH

def get_all_batches():
    """Get all batch simulations from the database."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # Get column names
    cursor.execute('PRAGMA table_info(simulation_batches)')
    batch_columns = [col[1] for col in cursor.fetchall()]
    
    # Get all batches
    cursor.execute('SELECT * FROM simulation_batches ORDER BY timestamp DESC')
    batch_rows = cursor.fetchall()
    
    batches = []
    for row in batch_rows:
        batch = {}
        for i, column in enumerate(batch_columns):
            if column == 'metadata':
                batch[column] = json.loads(row[i]) if row[i] else None
            else:
                batch[column] = row[i]
        batches.append(batch)
    
    conn.close()
    return batches

def get_batch_simulations(batch_id):
    """Get all simulations for a specific batch."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # Get the batch
    cursor.execute('SELECT * FROM simulation_batches WHERE id = ?', (batch_id,))
    batch_row = cursor.fetchone()
    
    if not batch_row:
        conn.close()
        return None
    
    # Get column names for batch
    cursor.execute('PRAGMA table_info(simulation_batches)')
    batch_columns = [col[1] for col in cursor.fetchall()]
    
    # Create batch dictionary
    batch = {}
    for i, column in enumerate(batch_columns):
        if column == 'metadata':
            batch[column] = json.loads(batch_row[i]) if batch_row[i] else None
        else:
            batch[column] = batch_row[i]
    
    # Get all simulations in the batch
    cursor.execute('''
        SELECT s.*, bs.sequence_number 
        FROM simulations s
        JOIN batch_simulations bs ON s.id = bs.simulation_id
        WHERE bs.batch_id = ?
        ORDER BY bs.sequence_number
    ''', (batch_id,))
    
    simulation_rows = cursor.fetchall()
    
    # Get column names for simulations
    cursor.execute('PRAGMA table_info(simulations)')
    simulation_columns = [col[1] for col in cursor.fetchall()]
    
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
    
    # Add simulations to batch
    batch['simulations'] = simulations
    
    conn.close()
    return batch

def get_entity_name(entity_id):
    """Get an entity's name by ID."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM entities WHERE id = ?', (entity_id,))
    result = cursor.fetchone()
    
    conn.close()
    return result[0] if result else f"Unknown Entity ({entity_id})"

def display_batches():
    """Display all batch simulations."""
    batches = get_all_batches()
    
    if not batches:
        print("No batch simulations found.")
        return
    
    print(f"\nFound {len(batches)} batch simulation(s):\n")
    print("-" * 80)
    for i, batch in enumerate(batches):
        print(f"{i+1}. {batch['name']} (ID: {batch['id']})")
        print(f"   Status: {batch['status']}")
        print(f"   Created: {batch['timestamp']}")
        print(f"   Description: {batch['description'] or 'N/A'}")
        print("-" * 80)
    
    choice = input("\nEnter batch number to view details (or 'q' to quit): ")
    if choice.lower() == 'q':
        return
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(batches):
            display_batch_details(batches[index]['id'])
        else:
            print(f"Invalid selection. Please choose a number between 1 and {len(batches)}.")
    except ValueError:
        print("Invalid input. Please enter a number or 'q'.")

def display_batch_details(batch_id):
    """Display details for a specific batch simulation."""
    batch = get_batch_simulations(batch_id)
    
    if not batch:
        print(f"Batch with ID {batch_id} not found.")
        return
    
    print("\n" + "=" * 80)
    print(f"BATCH: {batch['name']} (ID: {batch['id']})")
    print("=" * 80)
    print(f"Status: {batch['status']}")
    print(f"Created: {batch['timestamp']}")
    print(f"Description: {batch['description'] or 'N/A'}")
    print(f"Context: {batch['context']}")
    print("-" * 80)
    
    simulations = batch.get('simulations', [])
    if not simulations:
        print("No simulations found in this batch.")
        return
    
    print(f"Found {len(simulations)} simulation(s):\n")
    
    for i, simulation in enumerate(simulations):
        print(f"SIMULATION {i+1} (Sequence: {simulation['sequence_number']})")
        print(f"ID: {simulation['id']}")
        print(f"Type: {simulation['interaction_type']}")
        
        # Show entity names
        entity_ids = simulation['entity_ids']
        print("\nEntities:")
        for entity_id in entity_ids:
            entity_name = get_entity_name(entity_id)
            print(f"- {entity_name} (ID: {entity_id})")
        
        # Show content preview
        content = simulation['content']
        preview_length = 200
        preview = content[:preview_length] + ("..." if len(content) > preview_length else "")
        print("\nContent Preview:")
        print(preview)
        
        # Ask if user wants to see full content
        choice = input("\nShow full content? (y/n/q to quit): ")
        if choice.lower() == 'q':
            return
        elif choice.lower() == 'y':
            print("\nFULL CONTENT:")
            print(content)
            input("\nPress Enter to continue...")
        
        print("-" * 80)

def main():
    """Main entry point."""
    print("Batch Simulation Viewer")
    print("======================")
    
    while True:
        display_batches()
        choice = input("\nView more batches? (y/n): ")
        if choice.lower() != 'y':
            break

if __name__ == "__main__":
    main() 