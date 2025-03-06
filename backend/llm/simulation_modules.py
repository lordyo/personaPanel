"""
Simulation DSPy modules for the Entity Simulation Framework.

This module defines DSPy modules using proper class signatures for different types of entity interactions.
"""

import dspy
from typing import Dict, List, Any, Optional
import os
import json
import time
import logging
from functools import lru_cache

from .prompts import (
    SOLO_INTERACTION_PROMPT, 
    DYADIC_INTERACTION_PROMPT,
    GROUP_INTERACTION_PROMPT,
    format_entity_attributes,
    format_entity_description,
    format_entities_description
)

# Configure logging
logger = logging.getLogger(__name__)

# Configure retry parameters
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


class LLMError(Exception):
    """Exception raised for errors in LLM API calls."""
    pass


def retry_on_error(func):
    """
    Decorator to retry LLM API calls on failure.
    
    Args:
        func: Function to decorate
        
    Returns:
        Wrapped function with retry logic
    """
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < MAX_RETRIES:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                retries += 1
                if retries < MAX_RETRIES:
                    logger.warning(f"Error in LLM call: {str(e)}. Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Maximum retries reached. Last error: {str(e)}")
                    raise LLMError(f"Failed after {MAX_RETRIES} attempts: {str(e)}")
    return wrapper


# Define the class signatures as provided

class SoloInteractionSignature(dspy.Signature):
    """Generate a monologue by an entity in a specific context."""
    
    entity: Dict[str, Any] = dspy.InputField(
        desc="Entity instance with attributes including name, description, and personality traits"
    )
    context: str = dspy.InputField(
        desc="Detailed description of the situation or environment the entity is placed in. This can also be a task that the entity is given."
    )
    n_rounds: int = dspy.InputField(
        desc="Number of monologue segments to generate (default: 1)"
    )
    last_round_number: int = dspy.InputField(
        desc="The last round number from previous calls. New rounds should continue from this number. (default: 0, meaning start with round 1)"
    )
    previous_interaction: Optional[str] = dspy.InputField(
        desc="Previous interaction content, if this is a continuation of an earlier simulation"
    )
    
    content: str = dspy.OutputField(
        desc="Monologue by the entity in the context, including thoughts, feelings, and actions"
    )
    final_round_number: int = dspy.OutputField(
        desc="The number of the last round generated in this response. This will be used as last_round_number in subsequent calls."
    )


class DyadicInteractionSignature(dspy.Signature):
    """Generate dialogue between two entities in a specific context with multiple rounds of interaction."""
    
    entity1: Dict[str, Any] = dspy.InputField(
        desc="First entity instance with attributes including name, description, and personality traits"
    )
    entity2: Dict[str, Any] = dspy.InputField(
        desc="Second entity instance with attributes including name, description, and personality traits"
    )
    context: str = dspy.InputField(
        desc="Detailed description of the situation or environment where the entities interact. This can also be a task that the entities are given."
    )
    n_rounds: int = dspy.InputField(
        desc="Number of back-and-forth dialogue rounds between the entities to generate in this call (default: 1)"
    )
    last_round_number: int = dspy.InputField(
        desc="The last round number from previous calls. New rounds should continue from this number. (default: 0, meaning start with round 1)"
    )
    previous_interaction: Optional[str] = dspy.InputField(
        desc="Previous interaction content, if this is a continuation of an earlier conversation"
    )
    
    content: str = dspy.OutputField(
        desc="Dialogue between the two entities across multiple rounds. For each round, include inner thoughts and spoken dialogue. Format: ROUND [last_round_number+1]\n[entity1_name]: *[inner thoughts]*\n'[spoken dialogue]'\n[entity2_name]: *[inner thoughts]*\n'[spoken dialogue]'\n\nROUND [last_round_number+2]\n... Continue with all requested rounds, each clearly labeled with round number."
    )
    final_round_number: int = dspy.OutputField(
        desc="The number of the last round generated in this response. This will be used as last_round_number in subsequent calls."
    )


class GroupInteractionSignature(dspy.Signature):
    """Generate group discussion among multiple entities in a specific context with multiple rounds of interaction."""
    
    entities: List[Dict[str, Any]] = dspy.InputField(
        desc="List of entity instances, each with attributes including name, description, and personality traits"
    )
    context: str = dspy.InputField(
        desc="Detailed description of the situation or environment where the group interaction occurs. This can also be a task that the group is given."
    )
    n_rounds: int = dspy.InputField(
        desc="Number of back-and-forth dialogue rounds between the entities to generate in this call (default: 1)"
    )
    last_round_number: int = dspy.InputField(
        desc="The last round number from previous calls. New rounds should continue from this number. (default: 0, meaning start with round 1)"
    )
    previous_interaction: Optional[str] = dspy.InputField(
        desc="Previous interaction content, if this is a continuation of an earlier group discussion"
    )
    
    content: str = dspy.OutputField(
        desc="Group conversation across multiple rounds. For each round, include inner thoughts and spoken dialogue for each entity. Format: ROUND [last_round_number+1]\n[entity1_name]: *[inner thoughts]*\n'[spoken dialogue]'\n[entity2_name]: *[inner thoughts]*\n'[spoken dialogue]'\n...\n\nROUND [last_round_number+2]\n... Continue with all requested rounds, each clearly labeled with round number."
    )
    final_round_number: int = dspy.OutputField(
        desc="The number of the last round generated in this response. This will be used as last_round_number in subsequent calls."
    )


# Implement the simulation modules using the signatures

class SoloInteractionSimulator(dspy.Module):
    """DSPy module for simulating solo entity interactions."""
    
    def __init__(self):
        super().__init__()
        self.simulator = dspy.Predict(SoloInteractionSignature)
    
    @retry_on_error
    def forward(self, entity, context, n_rounds=1, last_round_number=0, previous_interaction=None):
        """
        Generate a narrative for a solo entity interaction.
        
        Args:
            entity: Entity instance with attributes
            context: The context description
            n_rounds: Number of monologue segments to generate (default: 1)
            last_round_number: The last round number from previous calls (default: 0)
            previous_interaction: Optional previous interaction content
            
        Returns:
            DSPy prediction with content and final_round_number
        """
        return self.simulator(
            entity=entity,
            context=context,
            n_rounds=n_rounds,
            last_round_number=last_round_number,
            previous_interaction=previous_interaction
        )


class DyadicInteractionSimulator(dspy.Module):
    """DSPy module for simulating interactions between two entities."""
    
    def __init__(self):
        super().__init__()
        self.simulator = dspy.Predict(DyadicInteractionSignature)
    
    @retry_on_error
    def forward(self, entity1, entity2, context, n_rounds=1, last_round_number=0, previous_interaction=None):
        """
        Generate a narrative for an interaction between two entities.
        
        Args:
            entity1: First entity instance
            entity2: Second entity instance
            context: The context description
            n_rounds: Number of back-and-forth dialogue rounds (default: 1)
            last_round_number: The last round number from previous calls (default: 0)
            previous_interaction: Optional previous interaction content
            
        Returns:
            DSPy prediction with content and final_round_number
        """
        return self.simulator(
            entity1=entity1,
            entity2=entity2,
            context=context,
            n_rounds=n_rounds,
            last_round_number=last_round_number,
            previous_interaction=previous_interaction
        )


class GroupInteractionSimulator(dspy.Module):
    """DSPy module for simulating interactions among multiple entities."""
    
    def __init__(self):
        super().__init__()
        self.simulator = dspy.Predict(GroupInteractionSignature)
    
    @retry_on_error
    def forward(self, entities, context, n_rounds=1, last_round_number=0, previous_interaction=None):
        """
        Generate a narrative for a group interaction.
        
        Args:
            entities: List of entity instances
            context: The context description
            n_rounds: Number of back-and-forth dialogue rounds (default: 1)
            last_round_number: The last round number from previous calls (default: 0)
            previous_interaction: Optional previous interaction content
            
        Returns:
            DSPy prediction with content and final_round_number
        """
        return self.simulator(
            entities=entities,
            context=context,
            n_rounds=n_rounds,
            last_round_number=last_round_number,
            previous_interaction=previous_interaction
        ) 