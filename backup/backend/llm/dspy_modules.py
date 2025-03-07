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
from .dynamic_signature import create_dynamic_signature, EntityResult

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
                if retries < MAX_RETRIES:
                    print(f"Error in LLM call: {str(e)}. Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    print(f"Maximum retries reached. Last error: {str(e)}")
                    raise LLMError(f"Failed after {MAX_RETRIES} attempts: {str(e)}")
    return wrapper


class EntityGenerator(dspy.Module):
    """DSPy module for generating entity instances."""
    
    def __init__(self):
        super().__init__()
    
    def _generate_non_text_attributes(self, dimensions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate random values for non-text dimensions.
        
        Args:
            dimensions: List of dimension dictionaries
            
        Returns:
            Dictionary of attribute values keyed by dimension name
        """
        attributes = {}
        
        for dim in dimensions:
            dimension_type = dim.get('type', '')
            dimension_name = dim.get('name', '')
            
            if not dimension_name or dimension_type == 'text':
                # Skip dimensions without names or text dimensions
                continue
            
            if dimension_type == 'boolean':
                # Generate boolean based on true_percentage
                true_percentage = dim.get('true_percentage', 0.5)
                attributes[dimension_name] = random.random() < true_percentage
                
            elif dimension_type == 'categorical':
                # Select an option based on distribution_values if provided
                options = dim.get('options', [])
                if not options:
                    continue
                    
                distribution_values = dim.get('distribution_values', {})
                if distribution_values and all(option in distribution_values for option in options):
                    # Use provided distribution
                    weights = [distribution_values.get(option, 0) for option in options]
                    # Normalize weights to ensure they sum to 1
                    total = sum(weights)
                    if total > 0:
                        normalized_weights = [w/total for w in weights]
                        attributes[dimension_name] = random.choices(options, weights=normalized_weights, k=1)[0]
                    else:
                        # Fallback to uniform if weights sum to 0
                        attributes[dimension_name] = random.choice(options)
                else:
                    # Uniform selection if no distribution values
                    attributes[dimension_name] = random.choice(options)
                
            elif dimension_type in ['int', 'float']:
                # Generate a number based on the distribution
                min_val = float(dim.get('min_value', 0))
                max_val = float(dim.get('max_value', 100))
                distribution = dim.get('distribution', 'uniform')
                
                if distribution == 'uniform':
                    # Uniform distribution between min and max
                    if dimension_type == 'int':
                        attributes[dimension_name] = random.randint(int(min_val), int(max_val))
                    else:
                        attributes[dimension_name] = random.uniform(min_val, max_val)
                        
                elif distribution == 'normal':
                    # Normal distribution with mean at center of range and specified std_deviation
                    mean = (min_val + max_val) / 2
                    
                    # Use spread_factor if available (new approach) or fall back to std_deviation (legacy)
                    if 'spread_factor' in dim:
                        # Convert spread factor to appropriate standard deviation based on range
                        spread_factor = dim.get('spread_factor', 0.5)  # 0=concentrated, 1=spread
                        std_dev = spread_factor * (max_val - min_val) / 6
                    else:
                        # Legacy behavior: use specified std_deviation or default
                        std_dev = dim.get('std_deviation', (max_val - min_val) / 6)  # Default to range/6
                    
                    # Generate value and clip to min-max range
                    value = random.normalvariate(mean, std_dev)
                    value = max(min_val, min(max_val, value))
                    
                    if dimension_type == 'int':
                        attributes[dimension_name] = int(round(value))
                    else:
                        attributes[dimension_name] = value
                        
                elif distribution == 'skewed':
                    # Skewed distribution using exponential and adjusting with skew_factor
                    skew_factor = dim.get('skew_factor', 0)  # -5 to 5, 0 is symmetric
                    
                    if skew_factor == 0:
                        # No skew, use uniform
                        if dimension_type == 'int':
                            attributes[dimension_name] = random.randint(int(min_val), int(max_val))
                        else:
                            attributes[dimension_name] = random.uniform(min_val, max_val)
                    else:
                        # Generate a value from beta distribution and scale to range
                        # Adjust alpha and beta parameters based on skew_factor
                        if skew_factor < 0:  # Left skew
                            alpha = 1 + abs(skew_factor)
                            beta = 1.0
                        else:  # Right skew
                            alpha = 1.0
                            beta = 1 + abs(skew_factor)
                        
                        # Generate value from beta distribution (0 to 1) and scale to range
                        beta_value = random.betavariate(alpha, beta)
                        scaled_value = min_val + beta_value * (max_val - min_val)
                        
                        if dimension_type == 'int':
                            attributes[dimension_name] = int(round(scaled_value))
                        else:
                            attributes[dimension_name] = scaled_value
            
            # Handle legacy 'numerical' type for backward compatibility
            elif dimension_type == 'numerical':
                # Generate a random number within the min-max range
                min_val = float(dim.get('min_value', 0))
                max_val = float(dim.get('max_value', 100))
                
                # Handle integer vs float values
                if isinstance(min_val, int) and isinstance(max_val, int):
                    attributes[dimension_name] = random.randint(int(min_val), int(max_val))
                else:
                    attributes[dimension_name] = round(random.uniform(min_val, max_val), 2)
            
        return attributes
    
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
            
            # Determine text attributes to collect as output fields
            text_dimensions = [dim for dim in dimensions if dim['type'] == 'text']
            output_fields = []
            for dim in text_dimensions:
                output_fields.append({
                    'name': dim['name'],
                    'description': dim.get('description', f"The {dim['name']} of this entity")
                })
            
            # Create a dynamic signature class for this entity type
            EntitySignature = create_dynamic_signature(
                entity_type=entity_type, 
                entity_description=entity_description,
                dimensions=dimensions, 
                non_text_attributes=non_text_attributes,
                variability=variability,
                output_fields=output_fields
            )
            
            # Create a predictor with this signature class - use ChainOfThought for better reasoning
            predictor = dspy.ChainOfThought(EntitySignature)
            
            # Prepare input arguments
            input_args = {
                "entity_type": entity_type,
                "entity_description": entity_description,
                "variability": variability
            }
            
            # Add non-text attributes as inputs
            for attr_name, attr_value in non_text_attributes.items():
                input_args[f"attr_{attr_name}"] = attr_value
            
            # Debug: Print the input arguments
            print(f"Input arguments: {input_args}")
            
            # Make the prediction
            prediction = predictor(**input_args)
            
            # Debug: Print the prediction object
            print("Prediction result:")
            print(f"Type: {type(prediction).__name__}")
            print(f"Available attributes: {dir(prediction)}")
            
            # Try to print reasoning from ChainOfThought if available
            if hasattr(prediction, 'rationale'):
                print(f"Reasoning: {prediction.rationale}")
            
            # Use the EntityResult class to extract and structure the result
            entity_result = EntityResult.from_prediction(
                prediction=prediction,
                dimensions=dimensions,
                non_text_attributes=non_text_attributes,
                output_fields=output_fields
            )
            
            # Create the final result dictionary
            result = {
                "name": entity_result.name,
                "description": entity_result.description,
                "attributes": entity_result.attributes
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