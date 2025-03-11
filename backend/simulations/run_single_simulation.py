#!/usr/bin/env python3
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
