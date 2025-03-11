#!/usr/bin/env python3
"""
Fix duplicate batch entries by removing the pending batch when there's also an in_progress batch
with the same name.
"""

import sqlite3
import sys

# Database path
DB_PATH = "data/entity_sim.db"

def fix_duplicate_batches():
    """Find and fix duplicate batch simulations."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Find batches with the same name
    cursor.execute('''
    SELECT name, GROUP_CONCAT(id), COUNT(*) 
    FROM simulation_batches 
    GROUP BY name 
    HAVING COUNT(*) > 1
    ''')
    
    duplicates = cursor.fetchall()
    
    if not duplicates:
        print("No duplicate batches found.")
        conn.close()
        return
    
    print(f"Found {len(duplicates)} batches with duplicate names:")
    
    for name, ids, count in duplicates:
        print(f"\nBatch name: {name}")
        print(f"Count: {count}")
        
        id_list = ids.split(',')
        print("Details:")
        
        # Get details for each batch with this name
        batch_details = []
        for batch_id in id_list:
            cursor.execute(
                'SELECT id, status, created_at FROM simulation_batches WHERE id = ?', 
                (batch_id,)
            )
            details = cursor.fetchone()
            batch_details.append(details)
            print(f"  ID: {details[0]}, Status: {details[1]}, Created: {details[2]}")
        
        # Check if we should fix this duplicate
        pending_batches = [b for b in batch_details if b[1] == 'pending']
        in_progress_batches = [b for b in batch_details if b[1] == 'in_progress']
        
        if pending_batches and in_progress_batches:
            # We have both pending and in_progress batches
            print(f"  Action: Delete {len(pending_batches)} pending batches")
            
            for batch in pending_batches:
                batch_id = batch[0]
                # First delete from batch_simulations
                cursor.execute('DELETE FROM batch_simulations WHERE batch_id = ?', (batch_id,))
                # Then delete from simulation_batches
                cursor.execute('DELETE FROM simulation_batches WHERE id = ?', (batch_id,))
                print(f"  Deleted pending batch: {batch_id}")
        else:
            print("  Action: No automatic fix available (need both pending and in_progress)")
    
    # Commit changes
    conn.commit()
    conn.close()
    print("\nFixes applied successfully.")

if __name__ == "__main__":
    fix_duplicate_batches() 