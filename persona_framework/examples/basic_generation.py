"""
Basic example of generating personas using the GenAI Persona Framework.
"""
import os
import sys
import dspy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to the path so we can import the persona_framework
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from persona_framework.modules.dimension import DimensionRegistry
from persona_framework.modules.generator import PersonaGeneratorWithValidation
from persona_framework.modules.persona import PersonaLibrary
from persona_framework.utils.io import register_dimensions_from_file, save_personas_to_file


def main():
    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
    
    # Initialize DSPy with Claude using the correct format
    lm = dspy.LM('anthropic/claude-3-sonnet-20240229', api_key=api_key)
    dspy.configure(lm=lm)
    
    # Create a dimension registry and load default dimensions
    registry = DimensionRegistry()
    dimensions_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config", "dimensions", "default.yaml"
    )
    register_dimensions_from_file(dimensions_path, registry)
    
    print(f"Loaded {len(registry.list_dimensions())} dimensions")
    
    # Create a generator
    generator = PersonaGeneratorWithValidation(registry)
    
    # Generate personas
    print("Generating personas...")
    personas = generator.generate(num_personas=5, diversity_level="high")
    
    # Print the generated personas
    print(f"\nGenerated {len(personas)} personas:\n")
    for i, persona in enumerate(personas):
        print(f"Persona {i+1}: {persona.name}")
        print("-" * 40)
        print(persona.get_prompt_description())
        print("\n")
    
    # Save the personas to a file
    library = PersonaLibrary()
    for persona in personas:
        library.add(persona)
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "generated_personas.yaml")
    
    save_personas_to_file(library, output_path)
    print(f"Saved personas to {output_path}")


if __name__ == "__main__":
    main() 