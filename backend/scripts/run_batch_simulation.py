#!/usr/bin/env python3
"""
Script to run a batch simulation from the command line.

This script provides a convenient way to run a batch simulation without using the API.
"""

import os
import sys
import json
import logging
import argparse

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulations.batch_simulator import BatchSimulationConfig, run_batch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('batch_simulation.log')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run a batch simulation")
    parser.add_argument('--entities', type=str, required=True,
                      help='Comma-separated list of entity IDs or path to JSON file with entity IDs')
    parser.add_argument('--interaction-size', type=int, required=True,
                      help='Number of entities per interaction (1=solo, 2=dyadic, 3+=group)')
    parser.add_argument('--num-simulations', type=int, required=True,
                      help='Number of simulations to run in the batch')
    parser.add_argument('--context', type=str, required=True,
                      help='Context description or path to JSON file with context')
    parser.add_argument('--name', type=str, default="Command-Line Batch Simulation",
                      help='Name for the batch')
    parser.add_argument('--description', type=str, default=None,
                      help='Description for the batch')
    parser.add_argument('--n-turns', type=int, default=1,
                      help='Number of turns per simulation round')
    parser.add_argument('--simulation-rounds', type=int, default=1,
                      help='Number of simulation rounds')
    
    args = parser.parse_args()
    
    # Process entity IDs
    if os.path.isfile(args.entities):
        with open(args.entities, 'r') as f:
            if args.entities.endswith('.json'):
                entity_data = json.load(f)
                if isinstance(entity_data, list):
                    entity_ids = entity_data
                elif isinstance(entity_data, dict) and 'entity_ids' in entity_data:
                    entity_ids = entity_data['entity_ids']
                else:
                    entity_ids = []
            else:
                # Assume text file with one ID per line
                entity_ids = [line.strip() for line in f if line.strip()]
    else:
        # Assume comma-separated list
        entity_ids = [id.strip() for id in args.entities.split(',') if id.strip()]
    
    if not entity_ids:
        logger.error("No valid entity IDs provided")
        return
    
    # Process context
    if os.path.isfile(args.context):
        with open(args.context, 'r') as f:
            if args.context.endswith('.json'):
                context_data = json.load(f)
                if isinstance(context_data, str):
                    context = context_data
                elif isinstance(context_data, dict) and 'context' in context_data:
                    context = context_data['context']
                else:
                    context = str(context_data)
            else:
                # Assume text file
                context = f.read().strip()
    else:
        # Assume direct context string
        context = args.context
    
    # Create batch config
    config = BatchSimulationConfig(
        name=args.name,
        description=args.description,
        entity_ids=entity_ids,
        context=context,
        interaction_size=args.interaction_size,
        num_simulations=args.num_simulations,
        n_turns=args.n_turns,
        simulation_rounds=args.simulation_rounds
    )
    
    # Run the batch
    logger.info(f"Starting batch simulation with {args.num_simulations} simulations")
    logger.info(f"Entity IDs: {', '.join(entity_ids)}")
    logger.info(f"Interaction size: {args.interaction_size}")
    
    batch_id = run_batch(config)
    
    logger.info(f"Batch simulation completed with ID: {batch_id}")
    print(f"Batch simulation ID: {batch_id}")

if __name__ == "__main__":
    main() 