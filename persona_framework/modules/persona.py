"""
Persona module for the GenAI Persona Framework.
Defines the Persona class and related utilities.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class Trait:
    """A trait is a specific value for a dimension."""
    dimension: str
    value: Any
    explanation: Optional[str] = None


@dataclass
class Persona:
    """
    Represents a persona with a set of traits.
    A persona is a coherent collection of traits across defined dimensions.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    traits: List[Trait] = field(default_factory=list)
    backstory: str = ""
    additional_attributes: Dict[str, Any] = field(default_factory=dict)
    
    def get_trait(self, dimension: str) -> Optional[Trait]:
        """
        Get a trait by dimension name.
        
        Args:
            dimension: Name of the dimension
            
        Returns:
            Optional[Trait]: The trait if found, None otherwise
        """
        for trait in self.traits:
            if trait.dimension == dimension:
                return trait
        return None
    
    def get_trait_value(self, dimension: str) -> Optional[Any]:
        """
        Get a trait value by dimension name.
        
        Args:
            dimension: Name of the dimension
            
        Returns:
            Optional[Any]: The trait value if found, None otherwise
        """
        trait = self.get_trait(dimension)
        return trait.value if trait else None
    
    def add_trait(self, dimension: str, value: Any, explanation: Optional[str] = None) -> None:
        """
        Add a trait to the persona.
        
        Args:
            dimension: Name of the dimension
            value: Value for the dimension
            explanation: Optional explanation for the trait
        """
        # Remove existing trait for this dimension if it exists
        self.traits = [t for t in self.traits if t.dimension != dimension]
        
        # Add the new trait
        self.traits.append(Trait(dimension=dimension, value=value, explanation=explanation))
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Persona to a dictionary.
        
        Returns:
            Dict: Dictionary representation of the Persona
        """
        return {
            'id': self.id,
            'name': self.name,
            'traits': [
                {
                    'dimension': t.dimension,
                    'value': t.value,
                    'explanation': t.explanation
                }
                for t in self.traits
            ],
            'backstory': self.backstory,
            'additional_attributes': self.additional_attributes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Persona':
        """
        Create a Persona from a dictionary.
        
        Args:
            data: Dictionary containing persona data
            
        Returns:
            Persona: A new Persona instance
        """
        traits = []
        for t in data.get('traits', []):
            traits.append(Trait(
                dimension=t['dimension'],
                value=t['value'],
                explanation=t.get('explanation')
            ))
        
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data.get('name', ''),
            traits=traits,
            backstory=data.get('backstory', ''),
            additional_attributes=data.get('additional_attributes', {})
        )
    
    def get_prompt_description(self) -> str:
        """
        Generate a description of the persona suitable for use in prompts.
        
        Returns:
            str: A textual description of the persona
        """
        description = f"Name: {self.name}\n\n"
        
        description += "Traits:\n"
        for trait in self.traits:
            description += f"- {trait.dimension}: {trait.value}"
            if trait.explanation:
                description += f" ({trait.explanation})"
            description += "\n"
        
        description += f"\nBackstory:\n{self.backstory}\n"
        
        if self.additional_attributes:
            description += "\nAdditional Attributes:\n"
            for key, value in self.additional_attributes.items():
                description += f"- {key}: {value}\n"
        
        return description


class PersonaLibrary:
    """
    A collection of personas that can be saved, loaded, and managed.
    """
    def __init__(self):
        self.personas: Dict[str, Persona] = {}
    
    def add(self, persona: Persona) -> None:
        """
        Add a persona to the library.
        
        Args:
            persona: The persona to add
        """
        self.personas[persona.id] = persona
    
    def get(self, persona_id: str) -> Optional[Persona]:
        """
        Get a persona by ID.
        
        Args:
            persona_id: ID of the persona
            
        Returns:
            Optional[Persona]: The persona if found, None otherwise
        """
        return self.personas.get(persona_id)
    
    def remove(self, persona_id: str) -> bool:
        """
        Remove a persona from the library.
        
        Args:
            persona_id: ID of the persona to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        if persona_id in self.personas:
            del self.personas[persona_id]
            return True
        return False
    
    def list_personas(self) -> List[Persona]:
        """
        List all personas in the library.
        
        Returns:
            List[Persona]: List of all personas
        """
        return list(self.personas.values())
    
    def clear(self) -> None:
        """Clear all personas from the library."""
        self.personas.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the library to a dictionary.
        
        Returns:
            Dict: Dictionary representation of the library
        """
        return {
            'personas': [p.to_dict() for p in self.personas.values()]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonaLibrary':
        """
        Create a PersonaLibrary from a dictionary.
        
        Args:
            data: Dictionary containing library data
            
        Returns:
            PersonaLibrary: A new PersonaLibrary instance
        """
        library = cls()
        for p_data in data.get('personas', []):
            persona = Persona.from_dict(p_data)
            library.add(persona)
        return library 