"""
Interaction pipeline for the GenAI Persona Framework.
Implements utilities for interacting with personas.
"""
from typing import Dict, List, Optional, Any

import dspy

from persona_framework.modules.persona import Persona


class PersonaInteractionSignature(dspy.Signature):
    """Generate a response from a persona's perspective"""
    persona = dspy.InputField(desc="Persona details")
    context = dspy.InputField(desc="Context information")
    task = dspy.InputField(desc="Task to perform")
    response = dspy.OutputField(desc="Response from the persona's perspective")


class PersonaInteractionModule(dspy.Module):
    """
    DSPy module for generating responses from a persona's perspective.
    """
    def __init__(self):
        super().__init__()
        self.generate_response = dspy.ChainOfThought(PersonaInteractionSignature)
    
    def forward(self, persona: Persona, context: str, task: str) -> str:
        """
        Generate a response from a persona's perspective.
        
        Args:
            persona: The persona to generate a response from
            context: Context information
            task: Task to perform
            
        Returns:
            str: Response from the persona's perspective
        """
        # Format persona for the prompt
        persona_text = persona.get_prompt_description()
        
        # Generate response
        result = self.generate_response(
            persona=persona_text,
            context=context,
            task=task
        )
        
        return result.response


class MultiPersonaDiscussionSignature(dspy.Signature):
    """Generate a discussion between multiple personas"""
    personas = dspy.InputField(desc="List of personas participating in the discussion")
    topic = dspy.InputField(desc="Topic of discussion")
    format = dspy.InputField(desc="Format of the discussion (e.g., debate, conversation)")
    num_rounds = dspy.InputField(desc="Number of rounds of discussion")
    discussion = dspy.OutputField(desc="The generated discussion")


class MultiPersonaDiscussionModule(dspy.Module):
    """
    DSPy module for generating discussions between multiple personas.
    """
    def __init__(self):
        super().__init__()
        self.generate_discussion = dspy.ChainOfThought(MultiPersonaDiscussionSignature)
    
    def forward(self, personas: List[Persona], topic: str, format: str = "conversation", num_rounds: int = 3) -> str:
        """
        Generate a discussion between multiple personas.
        
        Args:
            personas: List of personas participating in the discussion
            topic: Topic of discussion
            format: Format of the discussion (e.g., debate, conversation)
            num_rounds: Number of rounds of discussion
            
        Returns:
            str: The generated discussion
        """
        # Format personas for the prompt
        personas_text = []
        for i, persona in enumerate(personas):
            personas_text.append(f"Persona {i+1}:\n{persona.get_prompt_description()}")
        
        personas_str = "\n\n".join(personas_text)
        
        # Generate discussion
        result = self.generate_discussion(
            personas=personas_str,
            topic=topic,
            format=format,
            num_rounds=num_rounds
        )
        
        return result.discussion 