"""
Generator module for the GenAI Persona Framework.
Implements the logic for generating personas.
"""
import random
import time
from typing import Dict, List, Optional, Set, Tuple, Any

import dspy

from persona_framework.modules.dimension import Dimension, DimensionRegistry
from persona_framework.modules.persona import Persona, Trait


class PersonaGenerationSignature(dspy.Signature):
    """Generate personas based on dimension definitions"""
    dimensions = dspy.InputField(desc="List of dimension definitions")
    num_personas = dspy.InputField(desc="Number of personas to generate")
    diversity_level = dspy.InputField(desc="Required diversity between personas (low/medium/high)")
    personas = dspy.OutputField(desc="List of generated personas with names, traits and backstories")


class PersonaGenerator(dspy.Module):
    """
    DSPy module for generating personas based on dimension definitions.
    """
    def __init__(self):
        super().__init__()
        self.generate_personas = dspy.ChainOfThought(PersonaGenerationSignature)
    
    def forward(self, dimensions: List[Dict], num_personas: int, diversity_level: str = "medium") -> List[Dict]:
        """
        Generate personas based on the provided dimensions.
        
        Args:
            dimensions: List of dimension definitions
            num_personas: Number of personas to generate
            diversity_level: Required diversity between personas (low/medium/high)
            
        Returns:
            List[Dict]: List of generated personas
        """
        # Format dimensions for the prompt
        formatted_dimensions = []
        for dim in dimensions:
            dim_str = f"- {dim['name']}: {dim['description']}"
            if 'constraints' in dim and 'allowed_values' in dim['constraints']:
                dim_str += f" (Possible values: {', '.join(dim['constraints']['allowed_values'])})"
            formatted_dimensions.append(dim_str)
        
        dimensions_text = "\n".join(formatted_dimensions)
        
        # Generate a random seed based on current timestamp to ensure uniqueness
        random_seed = int(time.time() * 1000) % 10000
        
        # Add specific instructions for the LLM
        prompt_instructions = f"""
You are creating unique and diverse personas with distinct traits. Follow these guidelines:
1. ALWAYS assign a name to each persona, making sure names are unique and diverse (different ethnicities, backgrounds, etc.)
2. For each dimension, provide a value that makes sense in context
3. Create a coherent backstory in paragraph form that integrates all traits
4. Make personas feel like real entities with depth and consistency
5. Ensure each persona is COMPLETELY DIFFERENT from others - vary traits, personalities, backgrounds
6. Use randomization seed {random_seed} to guide your creativity and ensure uniqueness
7. Format each persona exactly like this:

Persona 1: [Full Name]
- [Dimension1]: [Value1]
- [Dimension2]: [Value2]
...etc.

[Backstory in paragraph form]

Persona 2: [Full Name]
...and so on
"""

        # Generate personas using DSPy
        result = self.generate_personas(
            dimensions=f"{prompt_instructions}\n\nDimensions:\n{dimensions_text}",
            num_personas=num_personas,
            diversity_level=diversity_level
        )
        
        # Debug prints
        print("DEBUG: Type of result:", type(result))
        print("DEBUG: Result attributes:", dir(result))
        print("DEBUG: Type of result.personas:", type(result.personas))
        
        # Parse the string output into a list of personas
        personas_text = result.personas
        
        # Split the text into individual personas
        persona_blocks = personas_text.split("Persona ")[1:]  # Skip the first empty element
        
        personas = []
        for block in persona_blocks:
            lines = block.strip().split("\n")
            
            # Extract name from the first line (if available)
            name = ""
            if ":" in lines[0]:
                name = lines[0].split(":", 1)[1].strip()
            else:
                # Instead of fallback, raise an error for malformed output
                raise ValueError(f"Failed to parse persona name from block: {block[:50]}...")
            
            # Check that name is not empty
            if not name.strip():
                raise ValueError("Generated persona is missing a name")
            
            # Find where the backstory starts (after the traits)
            backstory_start = 0
            for i, line in enumerate(lines):
                if not line.startswith("-") and i > 0:
                    backstory_start = i
                    break
            
            # Extract traits
            traits = []
            for i in range(1, backstory_start):
                if lines[i].startswith("-"):
                    trait_line = lines[i][1:].strip()  # Remove the dash and whitespace
                    if ":" in trait_line:
                        dimension, value = trait_line.split(":", 1)
                        traits.append({
                            "dimension": dimension.strip(),
                            "value": value.strip(),
                            "explanation": ""
                        })
            
            # Extract backstory
            backstory = "\n".join(lines[backstory_start:]).strip()
            if not backstory:
                # Instead of fallback, raise an error for missing backstory
                raise ValueError(f"Generated persona '{name}' is missing a backstory")
            
            # Create persona dictionary
            persona_dict = {
                "name": name,
                "backstory": backstory,
                "traits": traits
            }
            
            personas.append(persona_dict)
        
        return personas


class PersonaGeneratorWithValidation:
    """
    High-level generator that includes validation and ensures diversity.
    """
    def __init__(self, dimension_registry: DimensionRegistry):
        self.dimension_registry = dimension_registry
        self.generator = PersonaGenerator()
    
    def generate(self, num_personas: int, diversity_level: str = "medium", 
                 max_attempts: int = 3) -> List[Persona]:
        """
        Generate and validate personas.
        
        Args:
            num_personas: Number of personas to generate
            diversity_level: Required diversity between personas (low/medium/high)
            max_attempts: Maximum number of generation attempts
            
        Returns:
            List[Persona]: List of valid personas
        """
        # Convert dimensions to dictionary format for the generator
        dimensions = []
        for dim_name in self.dimension_registry.list_dimensions():
            dimension = self.dimension_registry.get(dim_name)
            if dimension:
                dimensions.append(dimension.to_dict())
        
        # If no dimensions are provided, raise error instead of creating a fallback
        if not dimensions:
            raise ValueError("No dimensions provided for persona generation. At least one dimension is required.")
        
        # Try to generate valid personas
        for attempt in range(max_attempts):
            try:
                # Add randomization by setting a random diversity level for each request
                # if the user hasn't explicitly specified high diversity
                if diversity_level != "high":
                    # Randomly increase diversity to ensure different results each time
                    actual_diversity = random.choice(["medium", "high"])
                else:
                    actual_diversity = diversity_level
                
                print(f"Generation attempt {attempt+1} with diversity level: {actual_diversity}")
                
                # Add additional randomness by slightly modifying dimensions
                randomized_dimensions = dimensions.copy()
                for dim in randomized_dimensions:
                    if 'description' in dim:
                        # Add a random comment to the description to make each request unique
                        random_suffix = f" (Seed: {random.randint(1000, 9999)})"
                        dim['description'] = dim['description'].split(" (Seed:")[0] + random_suffix
                
                persona_dicts = self.generator(randomized_dimensions, num_personas, actual_diversity)
                
                # Convert to Persona objects
                personas = []
                for p_dict in persona_dicts:
                    # Check for required fields instead of using fallbacks
                    if not p_dict.get("name"):
                        raise ValueError(f"Generated persona is missing a name")
                    
                    if not p_dict.get("backstory"):
                        raise ValueError(f"Generated persona '{p_dict['name']}' is missing a backstory")
                    
                    personas.append(Persona.from_dict(p_dict))
                
                # Validate personas
                valid_personas = self._validate_personas(personas)
                
                # Check if we have enough valid personas
                if len(valid_personas) >= num_personas:
                    return valid_personas[:num_personas]
                
                # If we don't have enough, try to generate more
                additional_needed = num_personas - len(valid_personas)
                additional_dicts = self.generator(dimensions, additional_needed, diversity_level)
                
                # Check additional personas for required fields
                for p_dict in additional_dicts:
                    if not p_dict.get("name"):
                        raise ValueError(f"Generated additional persona is missing a name")
                    
                    if not p_dict.get("backstory"):
                        raise ValueError(f"Generated additional persona '{p_dict.get('name', 'unknown')}' is missing a backstory")
                
                additional_personas = [Persona.from_dict(p) for p in additional_dicts]
                
                # Validate the additional personas
                valid_additional = self._validate_personas(additional_personas)
                
                # Combine and return
                all_valid = valid_personas + valid_additional
                return all_valid[:num_personas]
                
            except Exception as e:
                print(f"Error generating personas (attempt {attempt+1}/{max_attempts}): {str(e)}")
                if attempt == max_attempts - 1:
                    raise Exception(f"Failed to generate valid personas after {max_attempts} attempts: {str(e)}")
                continue
        
        raise Exception(f"Failed to generate personas after {max_attempts} attempts")
    
    def _validate_personas(self, personas: List[Persona]) -> List[Persona]:
        """
        Validate a list of personas against dimension constraints.
        
        Args:
            personas: List of personas to validate
            
        Returns:
            List[Persona]: List of valid personas
        """
        valid_personas = []
        
        for persona in personas:
            is_valid = True
            
            # Check that name is present instead of generating a fallback
            if not persona.name:
                raise ValueError("Persona is missing a name and cannot be validated")
            
            # Check each trait against its dimension constraints
            for trait in persona.traits:
                dimension = self.dimension_registry.get(trait.dimension)
                
                if not dimension:
                    # Skip traits for dimensions that aren't in the registry
                    continue
                
                if not dimension.validate_value(trait.value):
                    is_valid = False
                    break
            
            if is_valid:
                valid_personas.append(persona)
        
        return valid_personas 