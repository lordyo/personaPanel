"""
DSPy module definitions for the Entity Simulation Framework.

This module defines the DSPy modules used for entity generation and simulation.
"""

import dspy
import os
import json
import time
import random
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


def create_entity_signature(entity_type: str, dimensions: List[Dict], non_text_attributes: Dict, variability: str = "medium", entity_description: str = ""):
    """
    Factory function to create a properly typed DSPy Signature class for entity generation.
    
    Args:
        entity_type: The entity type name
        dimensions: List of dimension dictionaries defining the entity
        non_text_attributes: Dictionary of pre-generated non-text attributes
        variability: Level of variability in generation
        entity_description: Optional description of the entity type
        
    Returns:
        A DSPy Signature class with properly typed inputs and outputs
    """
    class DynamicEntitySignature(dspy.Signature):
        """Generate a detailed and realistic entity of type: '{entity_type}'.
        
        Generate a cohesive and believable entity based on the provided attributes and description.
        The entity must have a NAME and DESCRIPTION, along with text attributes that match the provided non-text attributes.
        Ensure consistency between all attributes to create a realistic entity.
        
        Variability level: {variability} (use this to determine how conventional or unique the entity should be)."""
        
        def __init__(self):
            super().__init__()
            
            # Format the docstring with the entity type and variability
            self.__doc__ = self.__doc__.format(entity_type=entity_type, variability=variability)
            
            # Add the main input fields
            self.entity_type = dspy.InputField(desc="The type of entity or persona to create.")
            self.entity_description = dspy.InputField(desc="Description of the entity, character or persona.")
            self.variability = dspy.InputField(desc="The level of creativity to use for this generation - low (typical, average), medium (distinct but plausible), high (unique, unusual)")
            
            # Add each non-text attribute as a separate input field
            for attr_name, attr_value in non_text_attributes.items():
                # Find the dimension for this attribute to get description
                dim = next((d for d in dimensions if d['name'] == attr_name), None)
                desc = f"{dim['description']}: {attr_value}" if dim else f"The {attr_name} of the entity: {attr_value}"
                setattr(self, f"attr_{attr_name}", dspy.InputField(desc=desc))
            
            # Standard output fields
            self.name = dspy.OutputField(desc="A unique and appropriate name for this entity")
            self.description = dspy.OutputField(desc="A cohesive description and backstory of the entity")
            
            # Add each text attribute as a separate output field
            for dim in dimensions:
                if dim['type'] == 'text':
                    setattr(self, f"text_{dim['name']}", dspy.OutputField(desc=f"{dim['description']}"))
    
    return DynamicEntitySignature


class EntityGenerator(dspy.Module):
    """
    DSPy module for generating entity instances based on entity type definitions.
    """
    
    def __init__(self):
        """
        Initialize the entity generator module.
        """
        super().__init__()
        # The predictor will be created dynamically for each entity type
    
    def _generate_non_text_attributes(self, dimensions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate random values for non-text attributes based on their definitions.
        
        Args:
            dimensions: List of dimension dictionaries defining the entity
            
        Returns:
            Dictionary with randomly generated non-text attribute values
        """
        non_text_attributes = {}
        
        for dim in dimensions:
            # Skip text attributes - these will be generated by the LLM
            if dim['type'] == 'text':
                continue
                
            # Generate boolean attributes
            elif dim['type'] == 'boolean':
                non_text_attributes[dim['name']] = random.choice([True, False])
                
            # Generate categorical attributes
            elif dim['type'] == 'categorical' and dim.get('options'):
                non_text_attributes[dim['name']] = random.choice(dim['options'])
                
            # Generate numerical attributes
            elif dim['type'] == 'numerical':
                min_val = dim.get('min_value', 0)
                max_val = dim.get('max_value', 100)
                
                # Handle distribution types
                if dim.get('distribution') == 'normal':
                    # Normal distribution centered between min and max
                    mean = (min_val + max_val) / 2
                    std_dev = (max_val - min_val) / 6  # ~99.7% within range
                    value = random.normalvariate(mean, std_dev)
                    # Clip to ensure within range
                    value = max(min_val, min(max_val, value))
                else:
                    # Default to uniform distribution
                    value = random.uniform(min_val, max_val)
                
                # Format based on likely type (integer vs float)
                if all(isinstance(x, int) for x in [min_val, max_val]):
                    value = int(value)
                else:
                    # Round to 2 decimal places for readability
                    value = round(value, 2)
                    
                non_text_attributes[dim['name']] = value
        
        return non_text_attributes
    
    @retry_on_error
    def forward(self, entity_type: str, dimensions: List[Dict[str, Any]], variability: str = "medium", entity_description: str = "") -> Dict[str, Any]:
        """
        Generate an entity instance based on the entity type and dimensions.
        
        Args:
            entity_type: Name of the entity type
            dimensions: List of dimension dictionaries defining the entity
            variability: Level of variability in generation ("low", "medium", "high")
            entity_description: Optional description of the entity type
            
        Returns:
            Dictionary with name, description, and attributes for the generated entity
        """
        try:
            print(f"Generating entity of type {entity_type} with variability {variability}")
            
            # First generate non-text attributes randomly
            non_text_attributes = self._generate_non_text_attributes(dimensions)
            
            # Create a dynamic signature class for this entity type
            EntitySignature = create_entity_signature(entity_type, dimensions, non_text_attributes, variability, entity_description)
            
            # Create a predictor with this signature class - use ChainOfThought instead of Predict
            # to give the model more reasoning ability
            predictor = dspy.ChainOfThought(EntitySignature)
            
            # Prepare input arguments - each attribute gets its own arg
            input_args = {
                "entity_type": entity_type,
                "entity_description": entity_description,
                "variability": variability
            }
            
            for attr_name, attr_value in non_text_attributes.items():
                input_args[f"attr_{attr_name}"] = attr_value
            
            # Make the prediction using the prepared arguments
            prediction = predictor(**input_args)
            
            # Debug: Print the prediction object to see what fields it has
            print("Prediction object available fields:")
            print(dir(prediction))
            
            # Debug: Check if it has name and description explicitly
            print(f"Has name attribute: {'name' in dir(prediction)}")
            print(f"Has description attribute: {'description' in dir(prediction)}")
            
            # Print the raw prediction dict to see what we have
            print("Raw prediction dictionary:")
            if hasattr(prediction, 'toDict'):
                print(prediction.toDict())
            else:
                print("No toDict method found")
                
            # Try to access rationale if it exists (for ChainOfThought)
            if hasattr(prediction, 'rationale'):
                print(f"Rationale: {prediction.rationale}")
            
            # Explicitly access name and description to avoid attribute errors
            name = getattr(prediction, 'name', "Unnamed Entity")
            description = getattr(prediction, 'description', "No description available")
            
            # Combine all attributes (non-text + text)
            attributes = non_text_attributes.copy()
            
            # Add text attributes from the prediction
            for dim in dimensions:
                if dim['type'] == 'text':
                    field_name = f"text_{dim['name']}"
                    if hasattr(prediction, field_name):
                        attributes[dim['name']] = getattr(prediction, field_name)
            
            # Create the result with name, description, and all attributes
            result = {
                "name": name,
                "description": description,
                "attributes": attributes
            }
            
            return result
            
        except Exception as e:
            import traceback
            print(f"Error in entity generation: {str(e)}")
            traceback.print_exc()
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
            entities_str = "\n\n".join([f"Entity {i+1}:\n{format_entity_attributes(entity)}" 
                                      for i, entity in enumerate(entities)])
            
            # Generate simulation response
            prediction = self.simulate(
                entities=entities_str,
                context=context
            )
            
            return prediction.response
        except Exception as e:
            raise LLMError(f"Group interaction simulation failed: {str(e)}") 