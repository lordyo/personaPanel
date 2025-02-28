"""
GenAI Persona Framework

A DSPy-based framework for generating and utilizing AI personas.
"""

__version__ = '0.1.0'

from persona_framework.modules.dimension import (
    Dimension, DimensionType, ImportanceLevel, 
    Constraint, Dependency, DimensionRegistry
)
from persona_framework.modules.persona import (
    Persona, Trait, PersonaLibrary
)
from persona_framework.modules.generator import (
    PersonaGenerator, PersonaGeneratorWithValidation
)
from persona_framework.modules.validator import (
    PersonaValidator, ValidationResult
)
from persona_framework.pipelines.interaction_pipeline import (
    PersonaInteractionModule, MultiPersonaDiscussionModule
) 