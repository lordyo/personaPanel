"""
Simulation module for the Entity Simulation Framework.

This module provides the core simulation logic for entity interactions.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import uuid
import datetime
import logging
from llm.interaction_module import InteractionSimulator, LLMError

# Configure logging
logger = logging.getLogger(__name__)


class InteractionType(Enum):
    """Types of interactions that can occur in a simulation."""
    SOLO = "solo"
    DYADIC = "dyadic"
    GROUP = "group"


@dataclass
class Context:
    """
    Represents the context in which entities interact.
    
    Attributes:
        id: Unique identifier for the context
        description: Textual description of the context
        metadata: Optional additional structured data about the context
    """
    id: str
    description: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SimulationResult:
    """
    Represents the result of a simulation.
    
    Attributes:
        id: Unique identifier for the simulation result
        timestamp: When the simulation was run
        context_id: Reference to the context
        interaction_type: The type of interaction (solo, dyadic, group)
        entity_ids: List of entity IDs that participated
        content: The generated content from the simulation
        metadata: Optional additional data about the simulation
    """
    id: str
    timestamp: datetime.datetime
    context_id: str
    interaction_type: str
    entity_ids: List[str]
    content: str
    metadata: Optional[Dict[str, Any]] = None


class SimulationEngine:
    """
    Engine for running simulations between entities.
    
    This class coordinates the execution of simulations by preparing
    prompts, sending them to the LLM, and processing results.
    """
    
    def __init__(self):
        """Initialize the simulation engine."""
        self.simulator = InteractionSimulator()
    
    def create_context(self, description: str, metadata: Optional[Dict[str, Any]] = None) -> Context:
        """
        Create a new context for simulations.
        
        Args:
            description: Textual description of the context
            metadata: Optional additional structured data
            
        Returns:
            A new Context object
        """
        return Context(
            id=str(uuid.uuid4()),
            description=description,
            metadata=metadata
        )
    
    def run_simulation(
        self,
        context: Context,
        entities: List[Dict[str, Any]],
        interaction_type: InteractionType = InteractionType.SOLO,
        n_rounds: int = 1,
        last_round_number: int = 0,
        previous_interaction: Optional[str] = None
    ) -> SimulationResult:
        """
        Run a simulation with the given entities in the provided context.
        
        Args:
            context: The context in which the entities will interact
            entities: List of entity instances to include in the simulation
            interaction_type: The type of interaction to simulate
            n_rounds: Number of back-and-forth dialogue rounds (default: 1)
            last_round_number: The last round number from previous calls (default: 0)
            previous_interaction: Optional previous interaction content
            
        Returns:
            The result of the simulation
        """
        content = ""
        final_round_number = last_round_number
        entity_ids = [entity.get('id', f"unknown-{i}") for i, entity in enumerate(entities)]
        
        # If n_rounds > 1, update context to indicate this is a multi-round simulation
        context_description = context.description
        if n_rounds > 1 and not "ROUND" in context_description:
            context_description = f"{context_description}\n\nThis simulation should include {n_rounds} rounds of dialogue, starting from round {last_round_number + 1}."
            context = Context(
                id=context.id,
                description=context_description,
                metadata=context.metadata
            )
        
        try:
            # Validate entity count based on interaction type
            if interaction_type == InteractionType.SOLO and len(entities) != 1:
                raise ValueError("Solo interaction requires exactly one entity")
            elif interaction_type == InteractionType.DYADIC and len(entities) != 2:
                raise ValueError("Dyadic interaction requires exactly two entities")
            elif interaction_type == InteractionType.GROUP and len(entities) < 2:
                raise ValueError("Group interaction requires at least two entities")
            
            # Use the unified interaction simulator for all interaction types
            result = self.simulator.forward(
                entities=entities,
                context=context.description,
                n_turns=n_rounds,
                last_turn_number=last_round_number,
                previous_interaction=previous_interaction
            )
            
            content = result.content
            final_round_number = getattr(result, 'final_turn_number', last_round_number + n_rounds)
        
        except Exception as e:
            logger.error(f"Error in simulation: {str(e)}")
            # Return a minimal result with error information
            return SimulationResult(
                id=str(uuid.uuid4()),
                timestamp=datetime.datetime.now(),
                context_id=context.id,
                interaction_type=interaction_type.value,
                entity_ids=entity_ids,
                content=f"Error in simulation: {str(e)}",
                metadata={"error": str(e)}
            )
        
        # Create and return the simulation result
        return SimulationResult(
            id=str(uuid.uuid4()),
            timestamp=datetime.datetime.now(),
            context_id=context.id,
            interaction_type=interaction_type.value,
            entity_ids=entity_ids,
            content=content,
            metadata={
                "n_rounds": n_rounds,
                "last_round_number": last_round_number,
                "final_round_number": final_round_number,
                "previous_interaction": previous_interaction
            }
        ) 