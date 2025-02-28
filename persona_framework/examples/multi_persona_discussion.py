"""
Example of generating a discussion between multiple personas.
"""
import os
import sys
import dspy

# Add the parent directory to the path so we can import the persona_framework
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from persona_framework.modules.dimension import DimensionRegistry
from persona_framework.modules.generator import PersonaGeneratorWithValidation
from persona_framework.pipelines.interaction_pipeline import MultiPersonaDiscussionModule
from persona_framework.utils.io import register_dimensions_from_file


def main():
    # Initialize DSPy with Claude (using the correct approach)
    lm = dspy.LM('anthropic/claude-3-sonnet-20240229', api_key=os.environ.get('ANTHROPIC_API_KEY'))
    dspy.configure(lm=lm)
    
    # Create a dimension registry and load default dimensions
    registry = DimensionRegistry()
    dimensions_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config", "dimensions", "default.yaml"
    )
    register_dimensions_from_file(dimensions_path, registry)
    
    # Create a generator
    generator = PersonaGeneratorWithValidation(registry)
    
    # Generate personas
    print("Generating personas...")
    personas = generator.generate(num_personas=4, diversity_level="high")
    
    # Print the generated personas
    print(f"\nGenerated {len(personas)} personas for the discussion:\n")
    for i, persona in enumerate(personas):
        print(f"Persona {i+1}: {persona.name}")
        print("-" * 40)
        print(persona.get_prompt_description())
        print("\n")
    
    # Create a discussion module
    discussion_module = MultiPersonaDiscussionModule()
    
    # Generate a discussion
    print("Generating discussion...")
    topic = "The impact of artificial intelligence on society"
    format = "debate"
    num_rounds = 2
    
    discussion = discussion_module(
        personas=personas,
        topic=topic,
        format=format,
        num_rounds=num_rounds
    )
    
    # Print the discussion
    print("\n" + "=" * 80)
    print(f"DISCUSSION TOPIC: {topic}")
    print("=" * 80 + "\n")
    print(discussion)
    
    # Save the discussion to a file
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "discussion.txt")
    
    with open(output_path, 'w') as f:
        f.write(f"DISCUSSION TOPIC: {topic}\n")
        f.write("=" * 80 + "\n\n")
        f.write(discussion)
    
    print(f"\nSaved discussion to {output_path}")


if __name__ == "__main__":
    main() 