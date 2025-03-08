#!/usr/bin/env python3
"""
Test script for the extended interaction module with the new fields.

This script tests the InteractionSimulator with the newly added input fields:
- interaction_type: how the entities interact (talk, play, trade, fight)
- language: the output language
"""

import os
import sys
import json
import dspy
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the interaction module
from llm.interaction_module import InteractionSimulator, format_entity_for_prompt

# Configure DSPy
def configure_dspy():
    """Configure DSPy with OpenAI GPT-4-mini for testing."""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please set it in your .env file.")
        sys.exit(1)
    
    # Configure DSPy with OpenAI's GPT-4o-mini (or alternative based on availability)
    try:
        model_name = "gpt-4o-mini"  # Use the recommended model from guidelines
        lm = dspy.LM(f"openai/{model_name}", api_key=api_key)
        dspy.configure(lm=lm)
        print(f"DSPy configured with {model_name}")
    except Exception as e:
        print(f"Error configuring DSPy with OpenAI: {str(e)}")
        print("Trying alternative configuration...")
        try:
            # Fallback to gpt-3.5-turbo if needed
            fallback_model = "gpt-3.5-turbo"
            lm = dspy.LM(f"openai/{fallback_model}", api_key=api_key)
            dspy.configure(lm=lm)
            print(f"DSPy configured with fallback model {fallback_model}")
        except Exception as e2:
            print(f"Failed to configure DSPy: {str(e2)}")
            sys.exit(1)

# Sample test entities
SAMPLE_ENTITIES = [
    {
        "name": "Dr. Emma Chen",
        "description": "A brilliant but socially awkward scientist",
        "attributes": {
            "intelligence": 0.9,
            "social_skills": 0.3,
            "patience": 0.7,
            "curiosity": 0.95,
            "field": "Quantum Physics"
        }
    },
    {
        "name": "Jack Morgan",
        "description": "A charismatic entrepreneur with big ideas",
        "attributes": {
            "intelligence": 0.75,
            "social_skills": 0.9,
            "patience": 0.4,
            "ambition": 0.85,
            "field": "Technology Startups"
        }
    }
]

# Sample test contexts
SAMPLE_CONTEXTS = [
    "At a technology conference after-party where attendees are networking.",
    "In a research lab where funding decisions for new projects are being made."
]

def test_interaction_simulator():
    """Test the InteractionSimulator with various configurations."""
    # Initialize the interaction simulator
    simulator = InteractionSimulator()
    
    # Test with default parameters (discussion in English)
    print("\n=== Test 1: Default Parameters (discussion in English) ===")
    result = simulator.forward(
        entities=SAMPLE_ENTITIES, 
        context=SAMPLE_CONTEXTS[0],
        n_turns=2
    )
    print(f"Output in English (discussion):\n{result.content}\n")
    print(f"Final turn number: {result.final_turn_number}\n")
    
    # Test with different interaction type (trading)
    print("\n=== Test 2: Trading Interaction ===")
    result = simulator.forward(
        entities=SAMPLE_ENTITIES, 
        context=SAMPLE_CONTEXTS[1],
        n_turns=2,
        interaction_type="trade"
    )
    print(f"Output (trade interaction):\n{result.content}\n")
    print(f"Final turn number: {result.final_turn_number}\n")
    
    # Test with different language (Spanish)
    print("\n=== Test 3: Different Language (Spanish) ===")
    result = simulator.forward(
        entities=SAMPLE_ENTITIES, 
        context=SAMPLE_CONTEXTS[0],
        n_turns=2,
        language="Spanish"
    )
    print(f"Output in Spanish:\n{result.content}\n")
    print(f"Final turn number: {result.final_turn_number}\n")
    
    # Test with both parameters customized (fight in German)
    print("\n=== Test 4: Custom Parameters (fight in German) ===")
    result = simulator.forward(
        entities=SAMPLE_ENTITIES, 
        context="In a debate about research funding priorities with limited resources.",
        n_turns=2,
        interaction_type="debate",
        language="German"
    )
    print(f"Output (debate in German):\n{result.content}\n")
    print(f"Final turn number: {result.final_turn_number}\n")

if __name__ == "__main__":
    print("Testing extended interaction module with new parameters...")
    configure_dspy()
    test_interaction_simulator()
    print("All tests completed!") 