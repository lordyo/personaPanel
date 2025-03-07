#!/usr/bin/env python3
"""
Simple DSPy test script to verify basic functionality.

This script tests basic DSPy functionality without the complexity of the 
full backend system. It creates a simple module and runs a prediction.
"""

import os
import sys
import json
import traceback
from dotenv import load_dotenv

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import DSPy
import dspy

# Configure DSPy with OpenAI
api_key = os.getenv("OPENAI_API_KEY")
model_name = os.getenv("DSPY_MODEL", "gpt-4o-mini")

if not api_key:
    print("Error: OPENAI_API_KEY not found in environment variables")
    sys.exit(1)

# Configure DSPy with OpenAI using the recommended approach
print(f"Configuring DSPy with model: openai/{model_name}")
try:
    # Changed from dspy.settings.configure and dspy.OpenAI to the updated pattern
    lm = dspy.LM(f"openai/{model_name}", api_key=api_key)
    dspy.configure(lm=lm)
    print("DSPy configuration successful")
except Exception as e:
    print(f"Error configuring DSPy: {e}")
    print(traceback.format_exc())
    sys.exit(1)

# Create a simple DSPy module for testing
class SimpleGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.Predict("instruction -> output")

    def forward(self, instruction):
        """Generate content based on the instruction."""
        return self.generate(instruction=instruction)


def main():
    """Run a simple test with DSPy."""
    print("Starting simple DSPy test...")
    
    # Create the module
    generator = SimpleGenerator()
    
    # Run a simple prediction
    print("Running prediction...")
    try:
        result = generator("Generate a short description of a fantasy character")
        
        # Print the result
        print("\nResult:")
        print("-" * 50)
        print(f"Output: {result.output}")
        print("-" * 50)
        
        print("\nTest complete!")
    except Exception as e:
        print(f"Error during prediction: {e}")
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main() 