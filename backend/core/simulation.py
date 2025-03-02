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
from backend.llm.simulation_modules import (
    SoloInteractionSimulator,
    DyadicInteractionSimulator,
    GroupInteractionSimulator
)

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
        self.solo_simulator = SoloInteractionSimulator()
        self.dyadic_simulator = DyadicInteractionSimulator()
        self.group_simulator = GroupInteractionSimulator()
    
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
        previous_interaction: Optional[str] = None
    ) -> SimulationResult:
        """
        Run a simulation with the given entities in the provided context.
        
        Args:
            context: The context in which the entities will interact
            entities: List of entity instances to include in the simulation
            interaction_type: The type of interaction to simulate
            previous_interaction: Optional previous interaction content
            
        Returns:
            The result of the simulation
        """
        content = ""
        scratchpad = ""
        entity_ids = [entity.get('id', f"unknown-{i}") for i, entity in enumerate(entities)]
        
        try:
            if interaction_type == InteractionType.SOLO:
                if len(entities) != 1:
                    raise ValueError("Solo interaction requires exactly one entity")
                
                # Use the solo interaction simulator
                result = self.solo_simulator(
                    entity=entities[0],
                    context=context.description,
                    previous_interaction=previous_interaction
                )
                content = result.content
                scratchpad = result.scratchpad
                
            elif interaction_type == InteractionType.DYADIC:
                if len(entities) != 2:
                    raise ValueError("Dyadic interaction requires exactly two entities")
                
                # Use the dyadic interaction simulator
                result = self.dyadic_simulator(
                    entity1=entities[0],
                    entity2=entities[1],
                    context=context.description,
                    previous_interaction=previous_interaction
                )
                content = result.content
                scratchpad = result.scratchpad
                
            elif interaction_type == InteractionType.GROUP:
                if len(entities) < 2:
                    raise ValueError("Group interaction requires at least two entities")
                
                # Use the group interaction simulator
                result = self.group_simulator(
                    entities=entities,
                    context=context.description,
                    previous_interaction=previous_interaction
                )
                content = result.content
                scratchpad = result.scratchpad
            
            else:
                raise ValueError(f"Unknown interaction type: {interaction_type}")
        
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
                "scratchpad": scratchpad,
                "previous_interaction": previous_interaction
            }
        ) 