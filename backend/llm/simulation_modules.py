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
    """Generate a narrative showing how an entity would respond to a specific context."""
    
    entity: Dict[str, Any] = dspy.InputField(
        desc="Entity instance with attributes including name, description, and personality traits"
    )
    context: str = dspy.InputField(
        desc="Detailed description of the situation or environment the entity is placed in"
    )
    previous_interaction: Optional[str] = dspy.InputField(
        desc="Previous interaction content, if this is a continuation of an earlier simulation"
    )
    
    content: str = dspy.OutputField(
        desc="Narrative describing how the entity responds to the context, including thoughts, feelings, and actions"
    )
    scratchpad: str = dspy.OutputField(
        desc="Brief notes that the entity would make about key points from this experience"
    )


class DyadicInteractionSignature(dspy.Signature):
    """Generate a dialogue and interaction between two entities in a specific context."""
    
    entity1: Dict[str, Any] = dspy.InputField(
        desc="First entity instance with attributes including name, description, and personality traits"
    )
    entity2: Dict[str, Any] = dspy.InputField(
        desc="Second entity instance with attributes including name, description, and personality traits"
    )
    context: str = dspy.InputField(
        desc="Detailed description of the situation or environment where the entities interact"
    )
    previous_interaction: Optional[str] = dspy.InputField(
        desc="Previous interaction content, if this is a continuation of an earlier conversation"
    )
    
    content: str = dspy.OutputField(
        desc="Narrative with dialogue describing the interaction between the two entities, including their reactions to each other"
    )
    scratchpad: str = dspy.OutputField(
        desc="Brief notes that each entity would make about key points from this interaction"
    )


class GroupInteractionSignature(dspy.Signature):
    """Generate a group discussion or interaction among multiple entities in a specific context."""
    
    entities: List[Dict[str, Any]] = dspy.InputField(
        desc="List of entity instances, each with attributes including name, description, and personality traits"
    )
    context: str = dspy.InputField(
        desc="Detailed description of the situation or environment where the group interaction occurs"
    )
    previous_interaction: Optional[str] = dspy.InputField(
        desc="Previous interaction content, if this is a continuation of an earlier group discussion"
    )
    
    content: str = dspy.OutputField(
        desc="Narrative with dialogue describing the group interaction, including how different entities contribute"
    )
    scratchpad: str = dspy.OutputField(
        desc="Brief notes that each entity would make about key points from this group interaction"
    )


# Implement the simulation modules using the signatures

class SoloInteractionSimulator(dspy.Module):
    """DSPy module for simulating solo entity interactions."""
    
    def __init__(self):
        super().__init__()
        self.simulator = dspy.ChainOfThought(SoloInteractionSignature)
    
    @retry_on_error
    def forward(self, entity, context, previous_interaction=None):
        """
        Generate a narrative for a solo entity interaction.
        
        Args:
            entity: Entity instance with attributes
            context: The context description
            previous_interaction: Optional previous interaction content
            
        Returns:
            DSPy prediction with content and scratchpad
        """
        return self.simulator(
            entity=entity,
            context=context,
            previous_interaction=previous_interaction
        )


class DyadicInteractionSimulator(dspy.Module):
    """DSPy module for simulating interactions between two entities."""
    
    def __init__(self):
        super().__init__()
        self.simulator = dspy.ChainOfThought(DyadicInteractionSignature)
    
    @retry_on_error
    def forward(self, entity1, entity2, context, previous_interaction=None):
        """
        Generate a narrative for an interaction between two entities.
        
        Args:
            entity1: First entity instance
            entity2: Second entity instance
            context: The context description
            previous_interaction: Optional previous interaction content
            
        Returns:
            DSPy prediction with content and scratchpad
        """
        return self.simulator(
            entity1=entity1,
            entity2=entity2,
            context=context,
            previous_interaction=previous_interaction
        )


class GroupInteractionSimulator(dspy.Module):
    """DSPy module for simulating interactions among multiple entities."""
    
    def __init__(self):
        super().__init__()
        self.simulator = dspy.ChainOfThought(GroupInteractionSignature)
    
    @retry_on_error
    def forward(self, entities, context, previous_interaction=None):
        """
        Generate a narrative for a group interaction.
        
        Args:
            entities: List of entity instances
            context: The context description
            previous_interaction: Optional previous interaction content
            
        Returns:
            DSPy prediction with content and scratchpad
        """
        return self.simulator(
            entities=entities,
            context=context,
            previous_interaction=previous_interaction
        ) 