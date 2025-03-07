import argparse

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run entity simulations")
    parser.add_argument('--entities', type=str, default='example_entities.json',
                        help='Path to entities configuration file')
    parser.add_argument('--config', type=str, default='example_simulation.json',
                        help='Path to simulation configuration file')
    parser.add_argument('--output-dir', type=str, default='../data/simulation_results',
                        help='Directory to save simulation results')
    args = parser.parse_args() 