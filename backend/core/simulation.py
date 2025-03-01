"""
Simulation module for the Entity Simulation Framework.

This module provides the core simulation logic for entity interactions.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import uuid
import datetime


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
    
    def __init__(self, llm_module):
        """
        Initialize the simulation engine.
        
        Args:
            llm_module: The LLM integration module to use for generating content
        """
        self.llm_module = llm_module
    
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
        interaction_type: InteractionType = InteractionType.SOLO
    ) -> SimulationResult:
        """
        Run a simulation with the given entities in the provided context.
        
        Args:
            context: The context in which the entities will interact
            entities: List of entity instances to include in the simulation
            interaction_type: The type of interaction to simulate
            
        Returns:
            The result of the simulation
        """
        # This is a stub implementation - the actual LLM integration
        # will be implemented in future sprints
        
        if interaction_type == InteractionType.SOLO:
            if len(entities) != 1:
                raise ValueError("Solo interaction requires exactly one entity")
                
            # In a real implementation, this would call the LLM
            content = f"Solo simulation for {entities[0]['name']} in context: {context.description}"
            
        elif interaction_type == InteractionType.DYADIC:
            if len(entities) != 2:
                raise ValueError("Dyadic interaction requires exactly two entities")
                
            # In a real implementation, this would call the LLM
            content = f"Dyadic simulation between {entities[0]['name']} and {entities[1]['name']} in context: {context.description}"
            
        elif interaction_type == InteractionType.GROUP:
            if len(entities) < 2:
                raise ValueError("Group interaction requires at least two entities")
                
            # In a real implementation, this would call the LLM
            entity_names = [entity['name'] for entity in entities]
            content = f"Group simulation with {', '.join(entity_names)} in context: {context.description}"
        
        else:
            raise ValueError(f"Unknown interaction type: {interaction_type}")
        
        return SimulationResult(
            id=str(uuid.uuid4()),
            timestamp=datetime.datetime.now(),
            context_id=context.id,
            interaction_type=interaction_type.value,
            entity_ids=[entity.get('id') for entity in entities],
            content=content
        ) 