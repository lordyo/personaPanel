"""
DSPy module definitions for the Entity Simulation Framework.

This module defines the DSPy modules used for entity generation and simulation.
"""

import dspy
from typing import Dict, List, Any, Optional
from .prompts import (
    ENTITY_GENERATION_PROMPT, 
    SOLO_INTERACTION_PROMPT, 
    DYADIC_INTERACTION_PROMPT,
    GROUP_INTERACTION_PROMPT,
    format_entity_attributes
)


class EntityGenerator(dspy.Module):
    """
    DSPy module for generating entity instances based on entity type definitions.
    """
    
    def __init__(self):
        """
        Initialize the entity generator module.
        """
        self.generate = dspy.ChainOfThought(
            "entity_type, dimensions, variability -> name, attributes"
        )
    
    def forward(self, entity_type: str, dimensions: List[Dict[str, Any]], variability: str = "medium") -> Dict[str, Any]:
        """
        Generate an entity instance based on the entity type and dimensions.
        
        Args:
            entity_type: Name of the entity type
            dimensions: List of dimension dictionaries defining the entity
            variability: Level of variability in generation ("low", "medium", "high")
            
        Returns:
            Dictionary with name and attributes for the generated entity
        """
        prompt = ENTITY_GENERATION_PROMPT.format(
            entity_type=entity_type,
            dimensions=dimensions,
            variability=variability
        )
        
        result = self.generate(
            entity_type=entity_type,
            dimensions=dimensions,
            variability=variability,
            prompt=prompt
        )
        
        # In a real implementation, this would parse and validate the result
        return result


class SoloInteractionSimulator(dspy.Module):
    """
    DSPy module for simulating solo entity interactions with a context.
    """
    
    def __init__(self):
        """
        Initialize the solo interaction simulator module.
        """
        self.simulate = dspy.ChainOfThought(
            "entity, context -> response"
        )
    
    def forward(self, entity: Dict[str, Any], context: str) -> str:
        """
        Simulate a solo interaction between an entity and a context.
        
        Args:
            entity: Entity instance dictionary
            context: Context description
            
        Returns:
            Generated response for the entity in the context
        """
        # Format the entity attributes for the prompt
        entity_attributes = format_entity_attributes(entity)
        
        # Create the prompt using the template
        prompt = SOLO_INTERACTION_PROMPT.format(
            entity=entity,
            entity_attributes=entity_attributes,
            context=context
        )
        
        result = self.simulate(
            entity=entity,
            context=context,
            prompt=prompt
        )
        
        # Return the generated response
        return result.response


class DyadicInteractionSimulator(dspy.Module):
    """
    DSPy module for simulating interactions between two entities in a context.
    """
    
    def __init__(self):
        """
        Initialize the dyadic interaction simulator module.
        """
        self.simulate = dspy.ChainOfThought(
            "entity1, entity2, context -> conversation"
        )
    
    def forward(self, entity1: Dict[str, Any], entity2: Dict[str, Any], context: str) -> str:
        """
        Simulate an interaction between two entities in a context.
        
        Args:
            entity1: First entity instance dictionary
            entity2: Second entity instance dictionary
            context: Context description
            
        Returns:
            Generated conversation between the two entities
        """
        # Format the entity attributes for the prompt
        entity1_attributes = format_entity_attributes(entity1)
        entity2_attributes = format_entity_attributes(entity2)
        
        # Create the prompt using the template
        prompt = DYADIC_INTERACTION_PROMPT.format(
            entity1=entity1,
            entity1_attributes=entity1_attributes,
            entity2=entity2,
            entity2_attributes=entity2_attributes,
            context=context
        )
        
        result = self.simulate(
            entity1=entity1,
            entity2=entity2,
            context=context,
            prompt=prompt
        )
        
        # Return the generated conversation
        return result.conversation


class GroupInteractionSimulator(dspy.Module):
    """
    DSPy module for simulating group interactions among multiple entities in a context.
    """
    
    def __init__(self):
        """
        Initialize the group interaction simulator module.
        """
        self.simulate = dspy.ChainOfThought(
            "entities, context -> discussion"
        )
    
    def forward(self, entities: List[Dict[str, Any]], context: str) -> str:
        """
        Simulate a group interaction among multiple entities in a context.
        
        Args:
            entities: List of entity instance dictionaries
            context: Context description
            
        Returns:
            Generated group discussion
        """
        # Create a formatted string of all entities with their attributes
        entity_details = []
        for i, entity in enumerate(entities):
            entity_detail = f"Entity {i+1}: {entity['name']}\n"
            entity_detail += format_entity_attributes(entity)
            entity_details.append(entity_detail)
        
        entity_details_str = "\n\n".join(entity_details)
        
        # Create the prompt using the template
        prompt = GROUP_INTERACTION_PROMPT.format(
            entity_details=entity_details_str,
            context=context
        )
        
        result = self.simulate(
            entities=entities,
            context=context,
            prompt=prompt
        )
        
        # Return the generated discussion
        return result.discussion 