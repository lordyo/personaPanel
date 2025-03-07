#!/usr/bin/env python3
"""
Simulation runner for entity interactions.

This script loads entity and simulation configurations from JSON files and
runs the specified simulation using the InteractionSimulator.
"""

import os
import sys
import json
import uuid
import argparse
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import dspy
from dotenv import load_dotenv

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.interaction_module import InteractionSimulator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('simulation_runner.log')
    ]
)
logger = logging.getLogger(__name__)

def load_config(file_path: str) -> Dict:
    """Load a configuration file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error loading config from {file_path}: {str(e)}")
        raise

def load_entities(entities_file: str, entity_ids: List[str] = None) -> List[Dict]:
    """
    Load entities from a JSON file.
    
    Args:
        entities_file: Path to the entities JSON file
        entity_ids: Optional list of entity IDs to filter by
        
    Returns:
        List of entity dictionaries
    """
    entities_config = load_config(entities_file)
    
    if 'entities' not in entities_config:
        raise ValueError(f"Entities file {entities_file} is missing 'entities' key")
    
    entities = entities_config['entities']
    
    # Filter entities by ID if specified
    if entity_ids:
        filtered_entities = []
        for entity_id in entity_ids:
            found = False
            for entity in entities:
                if entity.get('id') == entity_id:
                    filtered_entities.append(entity)
                    found = True
                    break
            if not found:
                logger.warning(f"Entity with ID {entity_id} not found in entities file")
        return filtered_entities
    
    return entities

def setup_dspy(llm_config=None):
    """Set up DSPy with the specified LLM configuration."""
    # Load environment variables if they haven't been loaded already
    load_dotenv()
    
    # If no specific configuration is provided, use environment variables
    if not llm_config:
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        openai_model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
        
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        llm_config = {
            'api_key': openai_api_key,
            'model': openai_model
        }
    
    # Configure DSPy with OpenAI
    model_string = f"openai/{llm_config['model']}"
    lm = dspy.LM(model_string, api_key=llm_config['api_key'])
    dspy.configure(lm=lm)
    
    logger.info(f"DSPy configured with model: {llm_config['model']}")

def run_simulation(
    entities: List[Dict],
    context: str,
    n_turns: int = 1,
    simulation_rounds: int = 1,
    output_file: Optional[str] = None
) -> Dict:
    """
    Run a complete simulation with the specified parameters.
    
    Args:
        entities: List of entity dictionaries
        context: The situation or environment description
        n_turns: Number of turns per simulation round
        simulation_rounds: Number of successive LLM calls
        output_file: Optional path to save the output
        
    Returns:
        Dictionary with simulation results
    """
    simulator = InteractionSimulator()
    
    # Initial state
    previous_interaction = None
    last_turn_number = 0
    all_content = []
    
    # Run each simulation round
    for round_idx in range(simulation_rounds):
        logger.info(f"Running simulation round {round_idx+1}/{simulation_rounds}")
        
        result = simulator(
            entities=entities,
            context=context,
            n_turns=n_turns,
            last_turn_number=last_turn_number,
            previous_interaction=previous_interaction
        )
        
        # Update for next round
        previous_interaction = result.content
        last_turn_number = result.final_turn_number
        all_content.append(result.content)
    
    # Combine all content
    combined_content = "\n\n".join(all_content)
    
    # Create result object
    simulation_result = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "context_id": str(uuid.uuid4()),  # In a real system, this might track the context
        "interaction_type": "solo" if len(entities) == 1 else "group",
        "entity_ids": [entity.get('id', 'unknown') for entity in entities],
        "content": combined_content,
        "metadata": {
            "n_turns": n_turns,
            "last_turn_number": 0,  # Starting point
            "final_turn_number": last_turn_number,  # End point
            "simulation_rounds": simulation_rounds,
            "previous_interaction": None  # No prior interaction at the start
        }
    }
    
    # Save to file if specified
    if output_file:
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(simulation_result, f, indent=2)
        logger.info(f"Saved result to {output_file}")
    
    return simulation_result

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run entity simulations")
    parser.add_argument('--entities', type=str, default='config/example_entities.json',
                        help='Path to entities configuration file')
    parser.add_argument('--config', type=str, default='config/example_simulation.json',
                        help='Path to simulation configuration file')
    parser.add_argument('--output-dir', type=str, default='data/simulation_results',
                        help='Directory to save simulation results')
    args = parser.parse_args()
    
    # Setup DSPy
    setup_dspy()
    
    # Load simulation config
    sim_config = load_config(args.config)
    
    # Extract parameters
    context = sim_config.get('context', 'A generic conversation')
    n_turns = sim_config.get('n_turns', 1)
    simulation_rounds = sim_config.get('simulation_rounds', 1)
    entity_ids = sim_config.get('entity_ids', [])
    
    # Load entities
    entities = load_entities(args.entities, entity_ids)
    
    if not entities:
        logger.error("No entities found or specified. Cannot run simulation.")
        return
    
    # Create output filename
    sim_type = "solo" if len(entities) == 1 else "group"
    entity_names = "_".join([entity.get('name', 'unnamed').split()[0].lower() for entity in entities])
    output_file = os.path.join(
        args.output_dir,
        f"{sim_type}_{entity_names}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    # Run simulation
    logger.info(f"Running {sim_type} simulation with {len(entities)} entities, "
                f"{n_turns} turns per round, {simulation_rounds} rounds")
    
    result = run_simulation(
        entities=entities,
        context=context,
        n_turns=n_turns,
        simulation_rounds=simulation_rounds,
        output_file=output_file
    )
    
    # Print a preview of the content
    content_preview = result['content'][:300] + "..." if len(result['content']) > 300 else result['content']
    print(f"\nSimulation completed successfully. Result saved to: {output_file}\n")
    print(f"Content preview:\n{content_preview}\n")

if __name__ == "__main__":
    main() 