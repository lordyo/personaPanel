#!/usr/bin/env python3
"""
Script to create a basic .env file for the Entity Simulation Framework.

This script creates a .env file with default values if it doesn't exist.
It prompts the user for the OpenAI API key.
"""

import os
import sys

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get the root directory (two levels up from this script)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_FILE = os.path.join(ROOT_DIR, '.env')
ENV_EXAMPLE_FILE = os.path.join(ROOT_DIR, '.env.example')


def create_env_file():
    """Create a .env file with default values if it doesn't exist."""
    if os.path.exists(ENV_FILE):
        print(f"\n.env file already exists at: {ENV_FILE}")
        overwrite = input("Do you want to overwrite it? (y/n): ").lower().strip()
        if overwrite != 'y':
            print("Operation cancelled. Existing .env file will not be modified.")
            return False
    
    # Check if .env.example exists
    if not os.path.exists(ENV_EXAMPLE_FILE):
        print(f"\nError: .env.example file not found at: {ENV_EXAMPLE_FILE}")
        print("Please create a .env.example file first.")
        return False
    
    # Ask for OpenAI API key
    api_key = input("\nEnter your OpenAI API Key (press Enter to skip): ").strip()
    
    # Read from .env.example
    with open(ENV_EXAMPLE_FILE, 'r') as f:
        env_example = f.readlines()
    
    # Create .env file
    with open(ENV_FILE, 'w') as f:
        for line in env_example:
            # Replace the OpenAI API key if provided
            if line.startswith('OPENAI_API_KEY=') and api_key:
                f.write(f'OPENAI_API_KEY={api_key}\n')
            else:
                f.write(line)
    
    print(f"\n.env file created successfully at: {ENV_FILE}")
    
    if not api_key:
        print("\nWarning: No OpenAI API key was provided.")
        print("Simulation features requiring the OpenAI API will not work.")
        print(f"You can add your key later by editing the .env file at: {ENV_FILE}")
    
    return True


def main():
    """Main function to run the script."""
    print("Entity Simulation Framework - Environment Setup")
    print("==============================================")
    
    create_env_file()


if __name__ == "__main__":
    main()