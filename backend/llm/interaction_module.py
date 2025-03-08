"""
Unified interaction module for the Entity Simulation Framework.

This module defines a single DSPy signature and module for entity interactions,
regardless of the number of entities involved (solo, dyadic, or group).
"""

import dspy
import logging
import time
from typing import Dict, List, Any, Optional
from functools import wraps

# Error handling
class LLMError(Exception):
    """Exception raised for errors in LLM calls."""
    pass

def retry_on_error(func):
    """Decorator to retry functions on error."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.error(f"Error in LLM call (attempt {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    logging.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logging.error(f"Failed after {max_retries} attempts")
                    raise LLMError(f"Failed after {max_retries} attempts: {str(e)}")
    return wrapper

# Format helper functions
def format_entity_for_prompt(entity):
    """Format an entity dictionary for inclusion in a prompt."""
    formatted = f"Name: {entity['name']}\nDescription: {entity['description']}\n"
    
    # Add attributes if present
    if 'attributes' in entity and entity['attributes']:
        formatted += "Attributes:\n"
        for key, value in entity['attributes'].items():
            # Format the value based on type
            if isinstance(value, (int, float)) and 0 <= value <= 1:
                # Convert 0-1 scale to descriptive text for better LLM understanding
                level = ""
                if value < 0.2: level = "very low"
                elif value < 0.4: level = "low"
                elif value < 0.6: level = "moderate"
                elif value < 0.8: level = "high"
                else: level = "very high"
                formatted += f"- {key}: {level} ({value})\n"
            else:
                formatted += f"- {key}: {value}\n"
    
    return formatted

class InteractionSignature(dspy.Signature):
    """Generate interactions among 1-n entities in a specific context with multiple turns of interaction."""
    
    entities: List[Dict[str, Any]] = dspy.InputField(
        desc="List of entity instances (1 to n), each with attributes including name, description and other traits"
    )
    context: str = dspy.InputField(
        desc="Detailed description of the situation or environment for the interaction"
    )
    n_turns: int = dspy.InputField(
        desc="Number of dialogue turns to generate in this call"
    )
    last_turn_number: int = dspy.InputField(
        desc="The last turn number from previous calls (default: 0, meaning start with turn 1)"
    )
    previous_interaction: Optional[str] = dspy.InputField(
        desc="Previous interaction content, if this is a continuation"
    )
    interaction_type: str = dspy.InputField(
        desc="Type of interaction between entities (e.g., talk, play, trade, fight)"
    )
    language: str = dspy.InputField(
        desc="Language to use for the output interaction"
    )
    
    content: str = dspy.OutputField(
        desc="Interaction content for each entity across all turns"
    )
    final_turn_number: int = dspy.OutputField(
        desc="The number of the last turn generated in this call"
    )

class InteractionSimulator(dspy.Module):
    """Module to simulate interactions between 1-n entities."""
    
    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(InteractionSignature)
    
    @retry_on_error
    def forward(self, entities, context, n_turns=1, last_turn_number=0, previous_interaction=None, interaction_type="discussion", language="English"):
        """Generate interactions between entities.
        
        Args:
            entities: List of entity dictionaries (can be a single entity)
            context: The situation or environment description
            n_turns: Number of dialogue turns to generate in this call
            last_turn_number: The last turn number from previous calls
            previous_interaction: Previous interaction content if continuing
            interaction_type: Type of interaction between entities (e.g., talk, play, trade, fight)
            language: Language to use for the output interaction
            
        Returns:
            dspy.Prediction with content and final_turn_number
        """
        # Make sure entities is a list
        if not isinstance(entities, list):
            entities = [entities]
            
        result = self.predictor(
            entities=entities,
            context=context,
            n_turns=n_turns,
            last_turn_number=last_turn_number,
            previous_interaction=previous_interaction,
            interaction_type=interaction_type,
            language=language
        )
        
        return result 