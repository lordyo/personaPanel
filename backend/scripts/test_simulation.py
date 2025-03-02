#!/usr/bin/env python3
"""
Test script for the Simulation Engine.

This script demonstrates how to run different types of simulations 
with hardcoded entity data.
"""

import os
import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv  # Add dotenv import

# Try to load .env file from project root
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
if env_path.exists():
    print(f"Loading environment variables from {env_path}")
    load_dotenv(dotenv_path=env_path)

# Add the parent directory to sys.path to import backend modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import dspy
from backend.core.simulation import SimulationEngine, InteractionType, Context
from backend.llm.simulation_modules import (
    SoloInteractionSimulator, 
    DyadicInteractionSimulator,
    GroupInteractionSimulator
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('simulation_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Setup DSPy with OpenAI
def setup_dspy():
    """Set up DSPy with OpenAI API key."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # Get model name from environment variable or use default
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    
    # Set up DSPy with LM using OpenAI
    lm = dspy.LM(f'openai/{model}', api_key=api_key)
    dspy.configure(lm=lm)
    logger.info(f"DSPy configured with OpenAI model: {model}")


# Sample entity data for testing
SAMPLE_ENTITIES = [
    {
        "id": "entity-001",
        "name": "Alex Chen",
        "attributes": {
            "age": 32,
            "profession": "Software Engineer",
            "personality": "Analytical, curious, and introverted. Alex enjoys solving complex problems and tends to think deeply before speaking.",
            "background": "Grew up in a tech-focused household and pursued computer science from an early age. Has worked for several tech startups and values innovation.",
            "goals": "To create meaningful technology that improves people's lives while maintaining a healthy work-life balance."
        }
    },
    {
        "id": "entity-002",
        "name": "Morgan Taylor",
        "attributes": {
            "age": 28,
            "profession": "Marketing Specialist",
            "personality": "Creative, outgoing, and persuasive. Morgan is quick-thinking and enjoys collaborative environments.",
            "background": "Studied communications and worked in various marketing roles. Has a talent for understanding consumer psychology and trends.",
            "goals": "To lead innovative marketing campaigns and eventually start a consulting agency."
        }
    },
    {
        "id": "entity-003",
        "name": "Jordan Rivera",
        "attributes": {
            "age": 45,
            "profession": "Clinical Psychologist",
            "personality": "Empathetic, patient, and observant. Jordan has a calming presence and listens more than speaks.",
            "background": "Became interested in psychology after volunteering with crisis support services. Has a private practice and also teaches part-time.",
            "goals": "To help people overcome mental health challenges and reduce stigma around seeking help."
        }
    }
]


def run_solo_simulation():
    """Test solo interaction simulation."""
    logger.info("Running solo simulation test")
    
    # Create engine and context
    engine = SimulationEngine()
    context = engine.create_context(
        "A coffee shop on a rainy morning. The atmosphere is quiet and contemplative, with soft jazz playing in the background."
    )
    
    # Run simulation with the first entity
    result = engine.run_simulation(
        context=context,
        entities=[SAMPLE_ENTITIES[0]],
        interaction_type=InteractionType.SOLO
    )
    
    # Display results
    print("\n" + "="*80)
    print(f"SOLO SIMULATION RESULT: {SAMPLE_ENTITIES[0]['name']}")
    print("-"*80)
    print(f"CONTEXT: {context.description}")
    print("-"*80)
    print(result.content)
    print("-"*80)
    print(f"SCRATCHPAD: {result.metadata.get('scratchpad', '')}")
    print("="*80 + "\n")
    
    return result


def run_dyadic_simulation():
    """Test dyadic interaction simulation."""
    logger.info("Running dyadic simulation test")
    
    # Create engine and context
    engine = SimulationEngine()
    context = engine.create_context(
        "A product design meeting where team members are discussing the direction for a new app. There's a whiteboard filled with ideas and sketches."
    )
    
    # Run simulation with the first two entities
    result = engine.run_simulation(
        context=context,
        entities=[SAMPLE_ENTITIES[0], SAMPLE_ENTITIES[1]],
        interaction_type=InteractionType.DYADIC
    )
    
    # Display results
    print("\n" + "="*80)
    print(f"DYADIC SIMULATION RESULT: {SAMPLE_ENTITIES[0]['name']} and {SAMPLE_ENTITIES[1]['name']}")
    print("-"*80)
    print(f"CONTEXT: {context.description}")
    print("-"*80)
    print(result.content)
    print("-"*80)
    print(f"SCRATCHPAD: {result.metadata.get('scratchpad', '')}")
    print("="*80 + "\n")
    
    return result


def run_group_simulation():
    """Test group interaction simulation."""
    logger.info("Running group simulation test")
    
    # Create engine and context
    engine = SimulationEngine()
    context = engine.create_context(
        "A community town hall meeting discussing the proposal for a new technology center in the neighborhood. The room is divided with some residents excited about the economic opportunities while others are concerned about gentrification."
    )
    
    # Run simulation with all three entities
    result = engine.run_simulation(
        context=context,
        entities=SAMPLE_ENTITIES,
        interaction_type=InteractionType.GROUP
    )
    
    # Display results
    print("\n" + "="*80)
    print(f"GROUP SIMULATION RESULT: {', '.join(entity['name'] for entity in SAMPLE_ENTITIES)}")
    print("-"*80)
    print(f"CONTEXT: {context.description}")
    print("-"*80)
    print(result.content)
    print("-"*80)
    print(f"SCRATCHPAD: {result.metadata.get('scratchpad', '')}")
    print("="*80 + "\n")
    
    return result


def run_continuation_test(previous_result):
    """Test continuation of a previous simulation."""
    logger.info("Running continuation simulation test")
    
    # Create engine and context
    engine = SimulationEngine()
    context = engine.create_context(
        "The meeting continues, but now the discussion has shifted to budget considerations and timeline constraints."
    )
    
    # Run simulation with the same entities as the previous result
    entity_ids = previous_result.entity_ids
    entities = [entity for entity in SAMPLE_ENTITIES if entity['id'] in entity_ids]
    
    result = engine.run_simulation(
        context=context,
        entities=entities,
        interaction_type=InteractionType(previous_result.interaction_type),
        previous_interaction=previous_result.content
    )
    
    # Display results
    print("\n" + "="*80)
    print(f"CONTINUATION SIMULATION RESULT")
    print("-"*80)
    print(f"CONTEXT: {context.description}")
    print("-"*80)
    print(result.content)
    print("-"*80)
    print(f"SCRATCHPAD: {result.metadata.get('scratchpad', '')}")
    print("="*80 + "\n")
    
    return result


def save_result_to_file(result, filename):
    """Save simulation result to a JSON file."""
    # Convert datetime to string for serialization
    result_dict = {
        "id": result.id,
        "timestamp": result.timestamp.isoformat(),
        "context_id": result.context_id,
        "interaction_type": result.interaction_type,
        "entity_ids": result.entity_ids,
        "content": result.content,
        "metadata": result.metadata
    }
    
    with open(filename, 'w') as f:
        json.dump(result_dict, f, indent=2)
    
    logger.info(f"Saved result to {filename}")


def main():
    """Run the simulation tests."""
    try:
        # Setup DSPy
        setup_dspy()
        
        # Create output directory
        os.makedirs("simulation_results", exist_ok=True)
        
        # Run solo simulation
        solo_result = run_solo_simulation()
        save_result_to_file(solo_result, "simulation_results/solo_result.json")
        
        # Run dyadic simulation
        dyadic_result = run_dyadic_simulation()
        save_result_to_file(dyadic_result, "simulation_results/dyadic_result.json")
        
        # Run group simulation
        group_result = run_group_simulation()
        save_result_to_file(group_result, "simulation_results/group_result.json")
        
        # Run continuation test based on dyadic result
        continuation_result = run_continuation_test(dyadic_result)
        save_result_to_file(continuation_result, "simulation_results/continuation_result.json")
        
        logger.info("All simulation tests completed successfully")
        
    except Exception as e:
        logger.error(f"Error running simulation tests: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 