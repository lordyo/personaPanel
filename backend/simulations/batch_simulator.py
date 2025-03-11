#!/usr/bin/env python3
"""
Batch Simulation Runner

This module provides functionality for running multiple simulations in parallel
as part of a simulation batch. It uses asyncio to handle concurrent simulation
execution with proper rate limiting to avoid overloading the LLM API.
"""

import os
import sys
import json
import uuid
import time
import asyncio
import logging
import itertools
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import math

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import storage
from llm.interaction_module import InteractionSimulator
from simulations.run_simulation import run_simulation, setup_dspy

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

# Maximum number of parallel simulations to run
MAX_PARALLEL_SIMULATIONS = int(os.getenv("MAX_PARALLEL_SIMULATIONS", "10"))

@dataclass
class BatchSimulationConfig:
    """Configuration for a batch simulation run."""
    name: str
    description: Optional[str]
    entity_ids: List[str]
    context: str
    interaction_size: int  # Number of entities per simulation
    num_simulations: int  # Number of simulations to run
    n_turns: int
    simulation_rounds: int
    metadata: Optional[Dict[str, Any]] = None


def generate_entity_combinations(entity_ids: List[str], k: int, max_combinations: int) -> List[List[str]]:
    """
    Generate combinations of entity IDs for simulations.
    
    Args:
        entity_ids: List of all entity IDs
        k: Number of entities per combination
        max_combinations: Maximum number of combinations to generate
        
    Returns:
        List of entity ID combinations
    """
    if k > len(entity_ids):
        raise ValueError(f"Cannot create combinations of {k} entities when only {len(entity_ids)} are available")
    
    all_combinations = list(itertools.combinations(entity_ids, k))
    
    # If there are fewer combinations than requested, return all of them
    if len(all_combinations) <= max_combinations:
        return [list(combo) for combo in all_combinations]
    
    # Otherwise, select a subset
    import random
    random.shuffle(all_combinations)
    return [list(combo) for combo in all_combinations[:max_combinations]]


def determine_interaction_type(interaction_size: int) -> str:
    """
    Determine the interaction type based on the number of entities.
    
    Args:
        interaction_size: Number of entities in the interaction
        
    Returns:
        Interaction type string ('solo', 'dyadic', or 'group')
    """
    if interaction_size == 1:
        return "solo"
    elif interaction_size == 2:
        return "dyadic"
    else:
        return "group"


async def run_simulation_async(
    entity_ids: List[str],
    context: str,
    n_turns: int,
    simulation_rounds: int,
    sequence_number: int,
    batch_id: str
) -> Tuple[Dict[str, Any], int]:
    """
    Run a single simulation asynchronously.
    
    Args:
        entity_ids: IDs of entities to include in the simulation
        context: Context description for the simulation
        n_turns: Number of turns per simulation round
        simulation_rounds: Number of simulation rounds
        sequence_number: Sequence number in the batch
        batch_id: ID of the containing batch
        
    Returns:
        Tuple of (simulation result dictionary, sequence number)
    """
    loop = asyncio.get_event_loop()
    
    # Load entities from storage
    entities = []
    for entity_id in entity_ids:
        entity = storage.get_entity(entity_id)
        if entity:
            entities.append(entity)
    
    if not entities:
        logger.error(f"No valid entities found for simulation {sequence_number} in batch {batch_id}")
        return {"error": "No valid entities found"}, sequence_number
    
    # Determine interaction type
    interaction_type = determine_interaction_type(len(entities))
    
    # Create a context object
    context_id = str(uuid.uuid4())
    storage.save_context(context_id, context)
    
    # Create a temporary file to store the simulation input and output
    import tempfile
    import subprocess
    
    try:
        # Create a temporary file for input
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as input_file:
            input_path = input_file.name
            # Prepare the input data
            input_data = {
                "entities": entities,
                "context": context,
                "n_turns": n_turns,
                "simulation_rounds": simulation_rounds
            }
            # Write input data to the file
            json.dump(input_data, input_file)
        
        # Create a temporary file for output
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as output_file:
            output_path = output_file.name
        
        # Run the simulation in a separate process
        logger.info(f"Running simulation {sequence_number} in separate process")
        
        # Path to the run_single_simulation.py script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, "run_single_simulation.py")
        
        # Make sure the script exists, or create it
        if not os.path.exists(script_path):
            logger.info(f"Creating run_single_simulation.py script at {script_path}")
            with open(script_path, 'w') as f:
                f.write('''#!/usr/bin/env python3
"""
Run a single simulation in a separate process.
This script is called by the batch simulator to avoid threading issues with DSPy.
"""

import sys
import json
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulations.run_simulation import run_simulation, setup_dspy

def main():
    """Run a simulation from input file and write results to output file."""
    if len(sys.argv) != 3:
        print("Usage: run_single_simulation.py <input_file> <output_file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        # Read input data
        with open(input_file, 'r') as f:
            input_data = json.load(f)
            
        # Extract simulation parameters
        entities = input_data["entities"]
        context = input_data["context"]
        n_turns = input_data["n_turns"]
        simulation_rounds = input_data["simulation_rounds"]
        
        # Setup DSPy in this process
        setup_dspy()
        
        # Run the simulation
        result = run_simulation(entities, context, n_turns, simulation_rounds, None)
        
        # Write result to output file
        with open(output_file, 'w') as f:
            json.dump(result, f)
            
        # Success
        sys.exit(0)
    except Exception as e:
        # Write error to output file
        with open(output_file, 'w') as f:
            json.dump({"error": str(e)}, f)
        sys.exit(1)

if __name__ == "__main__":
    main()
''')
        
        # Make the script executable
        os.chmod(script_path, 0o755)
        
        # Path to the Python interpreter in the virtual environment
        venv_dir = os.path.dirname(os.path.dirname(script_dir))
        python_path = os.path.join(venv_dir, "venv", "bin", "python3")
        
        # Run the simulation process
        cmd = [python_path, script_path, input_path, output_path]
        process = await loop.run_in_executor(None, lambda: subprocess.run(cmd, capture_output=True))
        
        if process.returncode != 0:
            logger.error(f"Simulation process failed with exit code {process.returncode}")
            logger.error(f"Error output: {process.stderr.decode('utf-8')}")
            return {"error": f"Simulation process failed: {process.stderr.decode('utf-8')}"}, sequence_number
        
        # Read the simulation result
        with open(output_path, 'r') as f:
            result = json.load(f)
            
        # Check for error in result
        if "error" in result:
            logger.error(f"Error in simulation {sequence_number}: {result['error']}")
            return {"error": result["error"]}, sequence_number
        
        # Save the simulation to the database
        simulation_id = storage.save_simulation(
            context_id=context_id,
            interaction_type=interaction_type,
            entity_ids=entity_ids,
            content=result["content"],
            metadata={
                "n_turns": n_turns,
                "simulation_rounds": simulation_rounds,
                "batch_id": batch_id,
                "sequence_number": sequence_number
            },
            final_turn_number=result["metadata"]["final_turn_number"]
        )
        
        # Add to batch
        storage.add_simulation_to_batch(batch_id, simulation_id, sequence_number)
        
        logger.info(f"Completed simulation {sequence_number} in batch {batch_id}")
        
        # Return the result and sequence number
        return {
            "id": simulation_id,
            "context_id": context_id,
            "entity_ids": entity_ids,
            "content": result["content"],
            "metadata": result["metadata"]
        }, sequence_number
        
    except Exception as e:
        logger.error(f"Error in simulation {sequence_number} in batch {batch_id}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e)}, sequence_number
    finally:
        # Clean up temporary files
        try:
            if os.path.exists(input_path):
                os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {str(e)}")


async def run_batch_simulations(config: BatchSimulationConfig, existing_batch_id: str = None) -> str:
    """
    Run a batch of simulations in parallel.
    
    Args:
        config: Batch simulation configuration
        existing_batch_id: Optional existing batch ID to use instead of creating a new one
        
    Returns:
        ID of the created or used batch
    """
    # Create a batch record or use existing one
    if existing_batch_id:
        batch_id = existing_batch_id
        logger.info(f"Using existing batch ID: {batch_id}")
    else:
        batch_id = storage.create_simulation_batch(
            name=config.name,
            description=config.description,
            context=config.context,
            metadata=config.metadata
        )
        logger.info(f"Created new batch with ID: {batch_id}")
    
    # Update batch status to in_progress
    storage.update_batch_status(batch_id, "in_progress")
    
    # Generate entity combinations
    try:
        entity_combinations = generate_entity_combinations(
            config.entity_ids,
            config.interaction_size,
            config.num_simulations
        )
    except ValueError as e:
        storage.update_batch_status(batch_id, "failed")
        logger.error(f"Error generating entity combinations: {str(e)}")
        return batch_id
    
    # If we got fewer combinations than requested, adjust num_simulations
    actual_num_simulations = min(len(entity_combinations), config.num_simulations)
    
    if actual_num_simulations < config.num_simulations:
        logger.warning(
            f"Requested {config.num_simulations} simulations but only {actual_num_simulations} "
            f"combinations are possible with {len(config.entity_ids)} entities and "
            f"interaction size {config.interaction_size}"
        )
    
    # Create a semaphore to limit concurrent API calls
    semaphore = asyncio.Semaphore(MAX_PARALLEL_SIMULATIONS)
    
    # Define a wrapper function that respects the semaphore
    async def run_with_semaphore(entity_ids, context, n_turns, simulation_rounds, sequence_number, batch_id):
        async with semaphore:
            return await run_simulation_async(
                entity_ids, context, n_turns, simulation_rounds, sequence_number, batch_id
            )
    
    # Create tasks for all simulations
    tasks = []
    for i, entity_combination in enumerate(entity_combinations[:actual_num_simulations]):
        tasks.append(
            run_with_semaphore(
                entity_combination,
                config.context,
                config.n_turns,
                config.simulation_rounds,
                i + 1,  # Sequence number (1-indexed)
                batch_id
            )
        )
    
    # Run all tasks concurrently and gather results
    results = []
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for exceptions in results
        success_count = 0
        for result, _ in results:
            if not isinstance(result, Exception) and "error" not in result:
                success_count += 1
        
        # Update batch status based on results
        if success_count == 0:
            storage.update_batch_status(batch_id, "failed")
        elif success_count < actual_num_simulations:
            storage.update_batch_status(batch_id, "partial")
        else:
            storage.update_batch_status(batch_id, "completed")
            
        logger.info(f"Batch {batch_id} completed: {success_count}/{actual_num_simulations} simulations successful")
        
    except Exception as e:
        storage.update_batch_status(batch_id, "failed")
        logger.error(f"Error running batch {batch_id}: {str(e)}")
    
    return batch_id


def run_batch(config: BatchSimulationConfig, existing_batch_id: str = None) -> str:
    """
    Run a batch of simulations. This is the main entry point for batch simulation.
    
    Args:
        config: Batch simulation configuration
        existing_batch_id: Optional existing batch ID to use instead of creating a new one
        
    Returns:
        ID of the created or used batch
    """
    # Run the async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        batch_id = loop.run_until_complete(run_batch_simulations(config, existing_batch_id))
        return batch_id
    finally:
        loop.close()


# Command-line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run batch simulations")
    parser.add_argument('--entities', type=str, required=True,
                        help='Comma-separated list of entity IDs or path to file with entity IDs')
    parser.add_argument('--interaction-size', type=int, required=True,
                        help='Number of entities per interaction (1=solo, 2=dyadic, 3+=group)')
    parser.add_argument('--num-simulations', type=int, required=True,
                        help='Number of simulations to run in the batch')
    parser.add_argument('--context', type=str, required=True,
                        help='Context description or path to file with context')
    parser.add_argument('--name', type=str, required=True,
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
                    raise ValueError("Invalid entity file format. Must be a JSON list or have 'entity_ids' key.")
            else:
                # Assume text file with one ID per line
                entity_ids = [line.strip() for line in f if line.strip()]
    else:
        # Assume comma-separated list
        entity_ids = [id.strip() for id in args.entities.split(',') if id.strip()]
    
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
                    raise ValueError("Invalid context file format. Must be a JSON string or have 'context' key.")
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
    batch_id = run_batch(config)
    
    logger.info(f"Batch simulation created with ID: {batch_id}")
    print(f"Batch simulation ID: {batch_id}") 