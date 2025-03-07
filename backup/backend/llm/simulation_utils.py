"""
Utility functions for simulations.

This module provides helper functions for running simulations with the 
Entity Simulation Framework.
"""

import logging
import uuid
import datetime
from typing import List, Dict, Any, Optional, Tuple

from backend.core.simulation import SimulationEngine, Context, InteractionType, SimulationResult

# Configure logging
logger = logging.getLogger(__name__)


def run_multi_round_simulation(
    entities: List[Dict[str, Any]],
    context_description: str,
    interaction_type: InteractionType,
    num_rounds: int,
    context_metadata: Optional[Dict[str, Any]] = None
) -> Tuple[List[SimulationResult], str]:
    """
    Run a multi-round simulation with the same entities and context but separate LLM calls.
    
    Each round builds upon the previous round's dialogue.
    
    Args:
        entities: List of entity instances to include in the simulation
        context_description: Description of the context for the simulation
        interaction_type: Type of interaction (SOLO, DYADIC, or GROUP)
        num_rounds: Number of rounds to simulate
        context_metadata: Optional metadata for the context
    
    Returns:
        Tuple containing:
          - List of SimulationResult objects, one for each round
          - Combined content string with all rounds concatenated
    """
    if num_rounds < 1:
        raise ValueError("Number of rounds must be at least 1")
    
    # Create simulation engine and context
    engine = SimulationEngine()
    context = engine.create_context(
        description=context_description,
        metadata=context_metadata
    )
    
    # Initialize results storage
    results = []
    combined_content = ""
    previous_interaction = None
    last_round_number = 0
    
    # Run the specified number of rounds
    for i in range(num_rounds):
        logger.info(f"Running simulation round {i+1}/{num_rounds}")
        
        # Run simulation for one round at a time
        result = engine.run_simulation(
            context=context,
            entities=entities,
            interaction_type=interaction_type,
            n_rounds=1,  # Each call is a single round
            last_round_number=last_round_number,
            previous_interaction=previous_interaction
        )
        
        # Store the result
        results.append(result)
        
        # Update previous interaction for next round
        previous_interaction = result.content
        
        # Update last_round_number for next round
        last_round_number = result.metadata.get('final_round_number', last_round_number + 1)
        
        # Add to combined content with round header
        round_header = f"\n\n{'='*20} ROUND {last_round_number} {'='*20}\n\n"
        combined_content += round_header + result.content
    
    logger.info(f"Completed all {num_rounds} rounds of simulation")
    return results, combined_content


def save_multi_round_simulation(
    results: List[SimulationResult],
    combined_content: str,
    base_context_id: str
) -> SimulationResult:
    """
    Create a combined SimulationResult from multiple rounds.
    
    Args:
        results: List of individual round results
        combined_content: Combined content from all rounds
        base_context_id: Context ID to associate with the combined result
    
    Returns:
        A new SimulationResult containing the combined information
    """
    if not results:
        raise ValueError("Must provide at least one simulation result")
    
    # Get information from the first result for consistency
    first_result = results[0]
    
    # Create metadata with information about the rounds
    metadata = {
        "num_rounds": len(results),
        "round_ids": [result.id for result in results],
        "is_multi_round": True
    }
    
    # Create the combined result
    combined_result = SimulationResult(
        id=str(uuid.uuid4()),
        timestamp=datetime.datetime.now(),
        context_id=base_context_id,
        interaction_type=first_result.interaction_type,
        entity_ids=first_result.entity_ids,
        content=combined_content,
        metadata=metadata
    )
    
    return combined_result 