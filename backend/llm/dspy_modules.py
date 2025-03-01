"""
DSPy module definitions for the Entity Simulation Framework.

This module defines the DSPy modules used for entity generation and simulation.
"""

import dspy
import os
import json
import time
from functools import lru_cache
from typing import Dict, List, Any, Optional
from .prompts import (
    ENTITY_GENERATION_PROMPT, 
    SOLO_INTERACTION_PROMPT, 
    DYADIC_INTERACTION_PROMPT,
    GROUP_INTERACTION_PROMPT,
    format_entity_attributes
)

# Configure caching directory
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

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
                if retries >= MAX_RETRIES:
                    raise LLMError(f"Failed after {MAX_RETRIES} attempts: {str(e)}")
                print(f"API call failed, retrying ({retries}/{MAX_RETRIES}): {str(e)}")
                time.sleep(RETRY_DELAY * retries)  # Exponential backoff
    return wrapper


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
        
    @retry_on_error
    @lru_cache(maxsize=100)  # Cache results for identical inputs
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
        try:
            # Convert dimensions to string for caching purposes
            dimensions_str = str(dimensions)
            
            # Check if we have a cached result
            cache_key = f"{entity_type}_{dimensions_str}_{variability}"
            cache_file = os.path.join(CACHE_DIR, f"{hash(cache_key)}.json")
            
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    return json.load(f)
            
            # Generate entity
            prediction = self.generate(
                entity_type=entity_type,
                dimensions=dimensions,
                variability=variability
            )
            
            result = {
                "name": prediction.name,
                "attributes": prediction.attributes
            }
            
            # Cache the result
            with open(cache_file, 'w') as f:
                json.dump(result, f)
                
            return result
        except Exception as e:
            raise LLMError(f"Entity generation failed: {str(e)}")


class SoloInteractionSimulator(dspy.Module):
    """
    DSPy module for simulating solo entity interactions within a context.
    """
    
    def __init__(self):
        """
        Initialize the solo interaction simulator.
        """
        self.simulate = dspy.ChainOfThought(
            "entity, context -> response"
        )
    
    @retry_on_error
    def forward(self, entity: Dict[str, Any], context: str) -> str:
        """
        Simulate how an entity would interact within a given context.
        
        Args:
            entity: Dictionary containing entity details
            context: Description of the context/scenario
            
        Returns:
            String containing the simulation result
        """
        try:
            # Format entity attributes for prompt
            entity_str = format_entity_attributes(entity)
            
            # Generate simulation response
            prediction = self.simulate(
                entity=entity_str,
                context=context
            )
            
            return prediction.response
        except Exception as e:
            raise LLMError(f"Solo interaction simulation failed: {str(e)}")


class DyadicInteractionSimulator(dspy.Module):
    """
    DSPy module for simulating interactions between two entities within a context.
    """
    
    def __init__(self):
        """
        Initialize the dyadic interaction simulator.
        """
        self.simulate = dspy.ChainOfThought(
            "entity1, entity2, context -> response"
        )
    
    @retry_on_error
    def forward(self, entity1: Dict[str, Any], entity2: Dict[str, Any], context: str) -> str:
        """
        Simulate how two entities would interact within a given context.
        
        Args:
            entity1: Dictionary containing first entity details
            entity2: Dictionary containing second entity details
            context: Description of the context/scenario
            
        Returns:
            String containing the simulation result
        """
        try:
            # Format entity attributes for prompt
            entity1_str = format_entity_attributes(entity1)
            entity2_str = format_entity_attributes(entity2)
            
            # Generate simulation response
            prediction = self.simulate(
                entity1=entity1_str,
                entity2=entity2_str,
                context=context
            )
            
            return prediction.response
        except Exception as e:
            raise LLMError(f"Dyadic interaction simulation failed: {str(e)}")


class GroupInteractionSimulator(dspy.Module):
    """
    DSPy module for simulating interactions among multiple entities within a context.
    """
    
    def __init__(self):
        """
        Initialize the group interaction simulator.
        """
        self.simulate = dspy.ChainOfThought(
            "entities, context -> response"
        )
    
    @retry_on_error
    def forward(self, entities: List[Dict[str, Any]], context: str) -> str:
        """
        Simulate how multiple entities would interact within a given context.
        
        Args:
            entities: List of dictionaries containing entity details
            context: Description of the context/scenario
            
        Returns:
            String containing the simulation result
        """
        try:
            # Format entities for prompt
            entities_str = ""
            for i, entity in enumerate(entities):
                entities_str += f"Entity {i+1}: {format_entity_attributes(entity)}\n\n"
            
            # Generate simulation response
            prediction = self.simulate(
                entities=entities_str,
                context=context
            )
            
            return prediction.response
        except Exception as e:
            raise LLMError(f"Group interaction simulation failed: {str(e)}") 