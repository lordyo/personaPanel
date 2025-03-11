#!/usr/bin/env python3
"""
Inspect batch simulations in the database and provide detailed information.
"""

import sqlite3
import sys
import json
from datetime import datetime
import os

# Database path
DB_PATH = "data/entity_sim.db"

def inspect_batches(batch_id=None, show_last=5):
    """
    Inspect batch simulations in the database.
    
    Args:
        batch_id: Optional specific batch ID to inspect
        show_last: Number of recent batches to show if no batch_id is provided
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()
    
    try:
        if batch_id:
            # Get specific batch
            cursor.execute(
                'SELECT * FROM simulation_batches WHERE id = ?', 
                (batch_id,)
            )
            batch = cursor.fetchone()
            
            if not batch:
                print(f"No batch found with ID: {batch_id}")
                return
                
            batches = [batch]
        else:
            # Get recent batches
            cursor.execute(
                'SELECT * FROM simulation_batches ORDER BY created_at DESC LIMIT ?', 
                (show_last,)
            )
            batches = cursor.fetchall()
            
            if not batches:
                print("No batches found in the database")
                return
        
        # Display batch information
        for batch in batches:
            print("\n" + "="*80)
            print(f"Batch ID:      {batch['id']}")
            print(f"Name:          {batch['name']}")
            print(f"Status:        {batch['status']}")
            print(f"Created:       {batch['created_at']}")
            print(f"Description:   {batch['description'] or 'None'}")
            
            # Parse metadata if available
            if batch['metadata']:
                try:
                    metadata = json.loads(batch['metadata'])
                    print(f"Metadata:      {json.dumps(metadata, indent=2)}")
                except json.JSONDecodeError:
                    print(f"Metadata:      [Error parsing JSON: {batch['metadata']}]")
            else:
                print("Metadata:      None")
                
            # Get simulations for this batch
            cursor.execute(
                '''
                SELECT s.*, bs.sequence_number 
                FROM simulations s
                JOIN batch_simulations bs ON s.id = bs.simulation_id
                WHERE bs.batch_id = ?
                ORDER BY bs.sequence_number
                ''', 
                (batch['id'],)
            )
            
            simulations = cursor.fetchall()
            print(f"\nComponent Simulations: {len(simulations)}")
            
            if not simulations:
                print("  No simulations found for this batch")
            else:
                print("\n  ID                                    | Seq | Entity Count | Final Turn")
                print("  " + "-"*75)
                
                for sim in simulations:
                    entity_ids = sim['entity_ids'].split(',') if sim['entity_ids'] else []
                    print(f"  {sim['id']} | {sim['sequence_number']:3d} | {len(entity_ids):12d} | {sim['final_turn_number'] or 0}")
            
            # Show context
            print(f"\nContext:")
            print(f"{batch['context']}\n")
            
    except Exception as e:
        print(f"Error inspecting batches: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Get batch ID from command line if provided
    batch_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    if batch_id:
        inspect_batches(batch_id)
    else:
        inspect_batches() 