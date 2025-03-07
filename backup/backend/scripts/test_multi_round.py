#!/usr/bin/env python3
"""
Test script for multi-round simulation functionality.

This script demonstrates both:
1. Single-prompt multi-round simulation (using n_rounds parameter)
2. Multiple-prompt round simulation (separate API calls building on previous dialogue)
"""

import os
import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Try to load .env file from project root
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
if env_path.exists():
    print(f"Loading environment variables from {env_path}")
    load_dotenv(dotenv_path=env_path)

# Add the parent directory to sys.path to import backend modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import dspy
from backend.core.simulation import SimulationEngine, InteractionType, Context
from backend.llm.simulation_utils import run_multi_round_simulation, save_multi_round_simulation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('multi_round_test.log')
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
    }
]


def test_single_prompt_multi_round():
    """
    Test multi-round simulation in a single prompt using the n_rounds parameter.
    This generates multiple back-and-forth exchanges in one LLM call.
    """
    logger.info("Running single-prompt multi-round test")
    
    # Create engine and context
    engine = SimulationEngine()
    context = engine.create_context(
        "A coffee shop on a quiet afternoon. Alex and Morgan are discussing potential collaboration on a new app idea."
    )
    
    # Run simulation with n_rounds=3
    result = engine.run_simulation(
        context=context,
        entities=[SAMPLE_ENTITIES[0], SAMPLE_ENTITIES[1]],
        interaction_type=InteractionType.DYADIC,
        n_rounds=3
    )
    
    # Display results
    print("\n" + "="*80)
    print(f"SINGLE-PROMPT MULTI-ROUND SIMULATION (3 rounds)")
    print("-"*80)
    print(f"CONTEXT: {context.description}")
    print("-"*80)
    print(result.content)
    print("="*80 + "\n")
    
    # Save result
    os.makedirs("multi_round_results", exist_ok=True)
    with open("multi_round_results/single_prompt_multi_round.json", 'w') as f:
        json.dump({
            "id": result.id,
            "timestamp": result.timestamp.isoformat(),
            "context_id": result.context_id,
            "interaction_type": result.interaction_type,
            "entity_ids": result.entity_ids,
            "content": result.content,
            "metadata": result.metadata
        }, f, indent=2)
    
    return result


def test_multi_prompt_simulation():
    """
    Test multi-round simulation with separate prompts.
    This makes separate LLM calls for each round, using previous output as context.
    """
    logger.info("Running multi-prompt simulation test")
    
    # Run multi-round simulation
    results, combined_content = run_multi_round_simulation(
        entities=[SAMPLE_ENTITIES[0], SAMPLE_ENTITIES[1]],
        context_description="A product design meeting. Alex and Morgan are brainstorming features for a new mobile app.",
        interaction_type=InteractionType.DYADIC,
        num_rounds=3,
        context_metadata={"meeting_type": "brainstorming", "location": "conference room"}
    )
    
    # Display results
    print("\n" + "="*80)
    print(f"MULTI-PROMPT SIMULATION (3 rounds)")
    print("-"*80)
    print(combined_content)
    print("="*80 + "\n")
    
    # Save individual rounds
    os.makedirs("multi_round_results", exist_ok=True)
    for i, result in enumerate(results):
        with open(f"multi_round_results/multi_prompt_round_{i+1}.json", 'w') as f:
            json.dump({
                "id": result.id,
                "timestamp": result.timestamp.isoformat(),
                "context_id": result.context_id,
                "interaction_type": result.interaction_type,
                "entity_ids": result.entity_ids,
                "content": result.content,
                "metadata": result.metadata
            }, f, indent=2)
    
    # Save combined result
    combined_result = save_multi_round_simulation(
        results=results,
        combined_content=combined_content,
        base_context_id=results[0].context_id
    )
    
    with open("multi_round_results/multi_prompt_combined.json", 'w') as f:
        json.dump({
            "id": combined_result.id,
            "timestamp": combined_result.timestamp.isoformat(),
            "context_id": combined_result.context_id,
            "interaction_type": combined_result.interaction_type,
            "entity_ids": combined_result.entity_ids,
            "content": combined_result.content,
            "metadata": combined_result.metadata
        }, f, indent=2)
    
    return results, combined_content


def main():
    """Run all multi-round simulation tests."""
    try:
        # Setup DSPy
        setup_dspy()
        
        # Test single-prompt multi-round simulation
        single_prompt_result = test_single_prompt_multi_round()
        
        # Test multi-prompt simulation
        multi_prompt_results, multi_prompt_content = test_multi_prompt_simulation()
        
        logger.info("All multi-round tests completed successfully")
        
    except Exception as e:
        logger.error(f"Error running multi-round tests: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 