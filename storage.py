from typing import List, Optional, Dict, Any
import sqlite3
import uuid
import json
import datetime

def save_simulation(
    context_id: str,
    interaction_type: str,
    entity_ids: List[str],
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    final_turn_number: Optional[int] = 0
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
        
    Returns:
        ID of the saved simulation
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    simulation_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()
    
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