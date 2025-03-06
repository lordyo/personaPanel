#!/usr/bin/env python3
"""
Simulation Runner Script.

This script runs simulations based on JSON configuration files.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
import datetime
from dotenv import load_dotenv  # Add dotenv import

# Try to load .env file from project root
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
if env_path.exists():
    print(f"Loading environment variables from {env_path}")
    load_dotenv(dotenv_path=env_path)

# Add the parent directory to sys.path to import backend modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import dspy
from backend.core.simulation import SimulationEngine, InteractionType, Context, SimulationResult

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


def load_json_file(filepath):
    """Load a JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def load_entities(filepath):
    """Load entity data from a JSON file."""
    try:
        return load_json_file(filepath)
    except Exception as e:
        logger.error(f"Error loading entities from {filepath}: {str(e)}")
        raise


def load_config(filepath):
    """Load simulation configuration from a JSON file."""
    try:
        return load_json_file(filepath)
    except Exception as e:
        logger.error(f"Error loading configuration from {filepath}: {str(e)}")
        raise


def save_result(result, output_dir, filename=None):
    """Save simulation result to a JSON file."""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simulation_{result.interaction_type}_{timestamp}.json"
    
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
    
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w') as f:
        json.dump(result_dict, f, indent=2)
    
    logger.info(f"Saved result to {filepath}")
    return filepath


def run_simulation_from_config(config, entities, output_dir):
    """Run a simulation based on a configuration."""
    logger.info(f"Running {config['interaction_type']} simulation")
    
    # Create simulation engine
    engine = SimulationEngine()
    
    # Create context
    context = engine.create_context(
        description=config['context']['description'],
        metadata=config['context'].get('metadata', {})
    )
    
    # Get entity data
    entity_ids = config['entity_ids']
    simulation_entities = []
    
    for entity_id in entity_ids:
        # Find entity by ID
        entity = next((e for e in entities if e.get('id') == entity_id), None)
        if not entity:
            raise ValueError(f"Entity with ID {entity_id} not found in the provided entities")
        simulation_entities.append(entity)
    
    # Get interaction type
    interaction_type_str = config['interaction_type'].upper()
    try:
        interaction_type = InteractionType[interaction_type_str]
    except KeyError:
        raise ValueError(f"Unknown interaction type: {config['interaction_type']}")
    
    # Get previous interaction if provided
    previous_interaction = config.get('previous_interaction')
    
    # Get number of rounds and last round number if provided
    n_rounds = config.get('n_rounds', 1)
    last_round_number = config.get('last_round_number', 0)
    
    # Run simulation
    result = engine.run_simulation(
        context=context,
        entities=simulation_entities,
        interaction_type=interaction_type,
        n_rounds=n_rounds,
        last_round_number=last_round_number,
        previous_interaction=previous_interaction
    )
    
    # Save result
    output_filename = config.get('output_filename')
    filepath = save_result(result, output_dir, output_filename)
    
    return result, filepath


def main():
    """Run the simulation from command line arguments."""
    parser = argparse.ArgumentParser(description='Run a simulation based on JSON configuration')
    parser.add_argument('--config', required=True, help='Path to the simulation configuration file')
    parser.add_argument('--entities', required=True, help='Path to the entities data file')
    parser.add_argument('--output-dir', default='simulation_results', help='Directory to save output')
    
    args = parser.parse_args()
    
    try:
        # Setup DSPy
        setup_dspy()
        
        # Load entities and configuration
        entities = load_entities(args.entities)
        config = load_config(args.config)
        
        # Run simulation
        result, filepath = run_simulation_from_config(config, entities, args.output_dir)
        
        # Display success message
        print(f"\nSimulation completed successfully. Result saved to: {filepath}")
        
        # Display a preview of the content
        print("\nContent preview:")
        preview_length = 200
        content_preview = result.content[:preview_length] + "..." if len(result.content) > preview_length else result.content
        print(content_preview)
        
    except Exception as e:
        logger.error(f"Error running simulation: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 