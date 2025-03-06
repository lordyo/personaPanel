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
        """You have been invited to give feedback on a movie script. It's a reimagining of 'The Thing', but told from the perspective of the creature.
        
        ## Script
        After drifting through the cold void for countless cycles, I crash upon a frozen world and enter hibernation. Awakened by strange bipedal creatures, I find myself exposed, vulnerable, and facing extinction. Their primitive thermal weapons burn through my cellular structure, but they fail to understand my nature—I am not one, but many, a collective that can divide, transform, and survive. Each of their cells I absorb teaches me more about their kind, allowing me to craft perfect replicas, indistinguishable from the originals. Their paranoia becomes my greatest weapon as they turn against each other, unable to discern friend from foe.
        Their isolation becomes my opportunity as I work methodically through their outpost. The brilliant one nearly discovers a test to reveal my presence, but I adapt faster than they anticipate. Their leader destroys their escape vessels, trapping us all in the endless white. As their numbers dwindle, I prepare for a long hibernation once more. Perhaps their rescue teams will arrive eventually, providing new vessels to continue my journey. In the final confrontation, two survivors sit in the burning ruins, watching each other with suspicion as the cold creeps in. Neither trusts the other, and it doesn't matter—the cold preserves, and I am patient. I have all the time in the universe.
        
        """
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
    print("="*80 + "\n")
    
    return result


def run_dyadic_simulation():
    """Test dyadic interaction simulation."""
    logger.info("Running dyadic simulation test")
    
    # Create engine and context
    engine = SimulationEngine()
    context = engine.create_context(
        """You are in a bar, discussing a novella idea a mutual friend of yours has given you. The friend, Jacob, is an aspiring writer.

        ## Novella Idea
        **Title:** Dinner for the Old Ones**

        Jenkins shuffled around the ancient dining table, carefully arranging five place settings though only Miss Blackwood remained alive to sit at one. "The same procedure as last year, madam?" he inquired, his voice barely audible above the howling winds that perpetually surrounded the Blackwood estate. The elderly woman nodded, her eyes reflecting the strange constellation visible through the warped glass of the dining room windows. Jenkins bowed stiffly before proceeding to the silver cabinet, his hands trembling not from age but from the knowledge of what the night would bring.

        As midnight approached, Jenkins served each empty chair in turn, pouring strange iridescent liquids and placing portions of food that writhed subtly upon ornate plates. "Admiral von Schneider," he announced to the first empty seat, where the air shimmered with an unnatural coldness. Moving to each position, Jenkins felt the familiar dread rising as he served "Mr. Winterbottom," "Sir Toby," and "Mr. Pommeroy"—names given long ago to entities that had no names in human tongues. With each serving, Jenkins consumed the offerings himself before moving to the next, his movements becoming increasingly erratic, his eyes bulging as otherworldly presences filled him, the ritual consumption binding the Old Ones to this plane for another year.

        Miss Blackwood watched with terrible serenity as Jenkins completed the final course, his body now merely a vessel for four ancient consciousnesses. The chandelier swayed without breeze, shadows elongated beyond natural angles, and the floorboards pulsed like the membrane of some vast organ. "The same procedure as every year, Jenkins," Miss Blackwood whispered as she rose, her silhouette blending with the darkness until only her eyes remained visible. Jenkins, no longer merely Jenkins, replied in a chorus of voices that seemed to emanate from the walls themselves: "The same procedure as every year, Miss Blackwood," before the dining room folded inward upon impossible geometries, and the annual communion with the Old Ones truly began.
        """
    )
    
    # Run simulation with the first two entities
    result = engine.run_simulation(
        context=context,
        entities=[SAMPLE_ENTITIES[0], SAMPLE_ENTITIES[1]],
        interaction_type=InteractionType.DYADIC,
        n_rounds=2  # Test with 2 rounds of dialogue
    )
    
    # Display results
    print("\n" + "="*80)
    print(f"DYADIC SIMULATION RESULT: {SAMPLE_ENTITIES[0]['name']} and {SAMPLE_ENTITIES[1]['name']} (2 rounds)")
    print("-"*80)
    print(f"CONTEXT: {context.description}")
    print("-"*80)
    print(result.content)
    print("="*80 + "\n")
    
    return result


def run_group_simulation():
    """Test group interaction simulation."""
    logger.info("Running group simulation test")
    
    # Create engine and context
    engine = SimulationEngine()
    context = engine.create_context(
        """You are on stage of a panel discussion at a local Comic Con. You have been given the topic of the first season of "Severance". """
    )
    
    # Run simulation with all three entities
    result = engine.run_simulation(
        context=context,
        entities=SAMPLE_ENTITIES,
        interaction_type=InteractionType.GROUP,
        n_rounds=2  # Test with 2 rounds of dialogue
    )
    
    # Display results
    print("\n" + "="*80)
    print(f"GROUP SIMULATION RESULT: {', '.join(entity['name'] for entity in SAMPLE_ENTITIES)} (2 rounds)")
    print("-"*80)
    print(f"CONTEXT: {context.description}")
    print("-"*80)
    print(result.content)
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
    print("="*80 + "\n")
    
    return result


def save_result_to_file(result, filename):
    """Save simulation result to a JSON file."""
    # Ensure output directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
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
        
        # Create output directory for results
        results_dir = "simulation_results"
        os.makedirs(results_dir, exist_ok=True)
        
        # Run solo simulation
        solo_result = run_solo_simulation()
        save_result_to_file(solo_result, f"{results_dir}/solo_result.json")
        
        # Run dyadic simulation
        dyadic_result = run_dyadic_simulation()
        save_result_to_file(dyadic_result, f"{results_dir}/dyadic_result.json")
        
        # Run group simulation
        group_result = run_group_simulation()
        save_result_to_file(group_result, f"{results_dir}/group_result.json")
        
        # Run continuation test based on dyadic result
        continuation_result = run_continuation_test(dyadic_result)
        save_result_to_file(continuation_result, f"{results_dir}/continuation_result.json")
        
        logger.info("All simulation tests completed successfully")
        
    except Exception as e:
        logger.error(f"Error running simulation tests: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 