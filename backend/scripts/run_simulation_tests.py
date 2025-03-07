#!/usr/bin/env python3
"""
Simulation tests for entity interactions.

This script runs tests for all combinations of:
- 1 or 3 entities
- 1 or 3 turns per round
- 1 or 2 simulation rounds
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run_simulation import load_entities, setup_dspy, run_simulation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('simulation_tests.log')
    ]
)
logger = logging.getLogger(__name__)

# Test configurations
TEST_CONFIGS = [
    # 1 entity, 1 turn, 1 round
    {
        "name": "solo_1turn_1round",
        "entity_count": 1,
        "turns": 1,
        "rounds": 1,
        "context": "A meditation retreat where participants are asked to reflect on their life journey."
    },
    # 1 entity, 3 turns, 1 round
    {
        "name": "solo_3turns_1round",
        "entity_count": 1,
        "turns": 3,
        "rounds": 1,
        "context": "A TED talk where the speaker is discussing their area of expertise."
    },
    # 1 entity, 1 turn, 2 rounds
    {
        "name": "solo_1turn_2rounds",
        "entity_count": 1,
        "turns": 1,
        "rounds": 2,
        "context": "A job interview where the candidate is asked to describe their greatest strengths and weaknesses."
    },
    # 1 entity, 3 turns, 2 rounds
    {
        "name": "solo_3turns_2rounds",
        "entity_count": 1,
        "turns": 3,
        "rounds": 2,
        "context": "A solo performance at an open mic night at a local café."
    },
    # 3 entities, 1 turn, 1 round
    {
        "name": "group_1turn_1round",
        "entity_count": 3,
        "turns": 1,
        "rounds": 1,
        "context": "A brief introduction session at a networking event for professionals from diverse industries."
    },
    # 3 entities, 3 turns, 1 round
    {
        "name": "group_3turns_1round",
        "entity_count": 3,
        "turns": 3,
        "rounds": 1,
        "context": "A panel discussion on work-life balance at a career development conference."
    },
    # 3 entities, 1 turn, 2 rounds
    {
        "name": "group_1turn_2rounds",
        "entity_count": 3,
        "turns": 1,
        "rounds": 2,
        "context": "A meeting where three people with different backgrounds are trying to resolve a conflict."
    },
    # 3 entities, 3 turns, 2 rounds
    {
        "name": "group_3turns_2rounds",
        "entity_count": 3,
        "turns": 3,
        "rounds": 2,
        "context": "A dinner party where three strangers with very different life philosophies discuss their views on success and happiness."
    }
]

def run_tests(entities_file, output_dir):
    """Run all test configurations."""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Load all entities
    all_entities = load_entities(entities_file)
    
    # Track results
    results = {}
    
    # Run each test configuration
    for config in TEST_CONFIGS:
        logger.info(f"Running test: {config['name']}")
        
        # Select entities for this test
        if config['entity_count'] == 1:
            # For solo tests, rotate through the entities for variety
            entity_index = TEST_CONFIGS.index(config) % len(all_entities)
            test_entities = [all_entities[entity_index]]
        else:
            # For group tests, use all entities
            test_entities = all_entities[:config['entity_count']]
        
        # Create output file path
        output_file = os.path.join(
            output_dir,
            f"test_{config['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        # Run the simulation
        try:
            result = run_simulation(
                entities=test_entities,
                context=config['context'],
                n_turns=config['turns'],
                simulation_rounds=config['rounds'],
                output_file=output_file
            )
            
            # Store success
            results[config['name']] = {
                "status": "success",
                "file": output_file
            }
            
            logger.info(f"Test {config['name']} completed successfully")
            
        except Exception as e:
            logger.error(f"Test {config['name']} failed: {str(e)}")
            
            # Store failure
            results[config['name']] = {
                "status": "failure",
                "error": str(e)
            }
    
    # Create summary report
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(TEST_CONFIGS),
        "successful_tests": sum(1 for r in results.values() if r["status"] == "success"),
        "failed_tests": sum(1 for r in results.values() if r["status"] == "failure"),
        "results": results
    }
    
    # Save summary
    summary_file = os.path.join(output_dir, f"test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    return summary

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run simulation tests")
    parser.add_argument('--entities', type=str, default='config/example_entities.json',
                        help='Path to entities configuration file')
    parser.add_argument('--output-dir', type=str, default='data/test_results',
                        help='Directory to save test results')
    args = parser.parse_args()
    
    # Setup DSPy
    setup_dspy()
    
    # Run tests
    summary = run_tests(args.entities, args.output_dir)
    
    # Print summary
    print("\n===== TEST SUMMARY =====")
    print(f"Total tests: {summary['total_tests']}")
    print(f"Successful: {summary['successful_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print("=======================\n")
    
    # Print detailed results
    for name, result in summary['results'].items():
        status = "✅" if result["status"] == "success" else "❌"
        print(f"{status} {name}")
        if result["status"] == "success":
            print(f"   Output: {result['file']}")
        else:
            print(f"   Error: {result['error']}")
    
    # Return exit code based on success
    return 0 if summary['failed_tests'] == 0 else 1

if __name__ == "__main__":
    sys.exit(main()) 