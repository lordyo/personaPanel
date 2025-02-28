"""
Validator module for the GenAI Persona Framework.
Implements validation utilities for personas.
"""
from typing import Dict, List, Optional, Tuple

import dspy

from persona_framework.modules.dimension import Dimension, DimensionRegistry
from persona_framework.modules.persona import Persona


class PersonaValidationSignature(dspy.Signature):
    """Validate a generated persona"""
    persona = dspy.InputField(desc="Persona to validate")
    dimension_constraints = dspy.InputField(desc="Constraints for each dimension")
    is_valid = dspy.OutputField(desc="Whether the persona is valid")
    issues = dspy.OutputField(desc="List of issues found, if any")
    suggestions = dspy.OutputField(desc="Suggestions for fixing issues, if any")


class PersonaCoherenceSignature(dspy.Signature):
    """Check if a persona's traits form a coherent whole"""
    persona = dspy.InputField(desc="Persona to check for coherence")
    coherence_score = dspy.OutputField(desc="Score from 0-10 indicating coherence")
    explanation = dspy.OutputField(desc="Explanation of the coherence score")
    suggestions = dspy.OutputField(desc="Suggestions for improving coherence, if any")


class PersonaValidator(dspy.Module):
    """
    DSPy module for validating personas.
    """
    def __init__(self):
        super().__init__()
        self.validate_persona = dspy.ChainOfThought(PersonaValidationSignature)
        self.check_coherence = dspy.ChainOfThought(PersonaCoherenceSignature)
    
    def validate(self, persona: Persona, dimension_registry: DimensionRegistry) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a persona against dimension constraints and check for coherence.
        
        Args:
            persona: The persona to validate
            dimension_registry: Registry of dimensions with constraints
            
        Returns:
            Tuple[bool, List[str], List[str]]: (is_valid, issues, suggestions)
        """
        # Format persona for the prompt
        persona_text = persona.get_prompt_description()
        
        # Format dimension constraints for the prompt
        constraints_text = []
        for dim_name in dimension_registry.list_dimensions():
            dimension = dimension_registry.get(dim_name)
            if dimension and dimension.constraints:
                constraint_str = f"- {dimension.name}: "
                
                if dimension.constraints.allowed_values:
                    constraint_str += f"Must be one of: {', '.join(dimension.constraints.allowed_values)}"
                
                if dimension.constraints.min_value is not None:
                    constraint_str += f"Minimum value: {dimension.constraints.min_value}"
                
                if dimension.constraints.max_value is not None:
                    constraint_str += f"Maximum value: {dimension.constraints.max_value}"
                
                constraints_text.append(constraint_str)
        
        constraints_str = "\n".join(constraints_text)
        
        # Validate persona
        validation_result = self.validate_persona(
            persona=persona_text,
            dimension_constraints=constraints_str
        )
        
        # Check coherence
        coherence_result = self.check_coherence(
            persona=persona_text
        )
        
        # Combine results
        is_valid = validation_result.is_valid and coherence_result.coherence_score >= 7
        
        issues = validation_result.issues
        if coherence_result.coherence_score < 7:
            issues.append(f"Low coherence score: {coherence_result.coherence_score}/10. {coherence_result.explanation}")
        
        suggestions = validation_result.suggestions + coherence_result.suggestions
        
        return is_valid, issues, suggestions


class ValidationResult:
    """
    Holds the result of a persona validation.
    """
    def __init__(self, is_valid: bool, issues: List[str], suggestions: List[str]):
        self.is_valid = is_valid
        self.issues = issues
        self.suggestions = suggestions
    
    def __bool__(self) -> bool:
        return self.is_valid 