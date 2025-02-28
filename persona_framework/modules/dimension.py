"""
Dimension module for the GenAI Persona Framework.
Defines the Dimension class and related utilities.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class DimensionType(Enum):
    """Types of dimensions that can be defined."""
    CATEGORICAL = "categorical"  # Limited set of categories
    NUMERIC = "numeric"  # Numeric values with possible range
    TEXT = "text"  # Free-form text values
    BOOLEAN = "boolean"  # True/False values


class ImportanceLevel(Enum):
    """Importance levels for dimensions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Dependency:
    """Defines a dependency between dimensions."""
    dimension: str  # Name of the dimension this depends on
    rule: str  # Natural language rule describing the dependency


@dataclass
class Constraint:
    """Constraints for dimension values."""
    # For categorical dimensions
    allowed_values: List[str] = field(default_factory=list)
    
    # For numeric dimensions
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    
    # For text dimensions
    max_length: Optional[int] = None
    format_regex: Optional[str] = None
    
    # For all dimensions
    custom_validation: Optional[str] = None


@dataclass
class Dimension:
    """
    Represents a dimension of a persona.
    A dimension is a specific attribute that can be used to define a persona.
    """
    name: str
    description: str
    dimension_type: DimensionType
    constraints: Optional[Constraint] = None
    importance: ImportanceLevel = ImportanceLevel.MEDIUM
    dependencies: List[Dependency] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    
    def validate_value(self, value: Any) -> bool:
        """
        Validates if a given value is valid for this dimension.
        
        Args:
            value: The value to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if self.constraints is None:
            return True
            
        if self.dimension_type == DimensionType.CATEGORICAL:
            if not self.constraints.allowed_values:
                return True
            return value in self.constraints.allowed_values
            
        elif self.dimension_type == DimensionType.NUMERIC:
            try:
                num_value = float(value)
                if self.constraints.min_value is not None and num_value < self.constraints.min_value:
                    return False
                if self.constraints.max_value is not None and num_value > self.constraints.max_value:
                    return False
                return True
            except (ValueError, TypeError):
                return False
                
        elif self.dimension_type == DimensionType.TEXT:
            if not isinstance(value, str):
                return False
            if self.constraints.max_length is not None and len(value) > self.constraints.max_length:
                return False
            # Regex validation would go here if implemented
            return True
            
        elif self.dimension_type == DimensionType.BOOLEAN:
            return isinstance(value, bool)
            
        return True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Dimension':
        """
        Create a Dimension from a dictionary (e.g., loaded from YAML).
        
        Args:
            data: Dictionary containing dimension data
            
        Returns:
            Dimension: A new Dimension instance
        """
        # Process dimension type
        dim_type = DimensionType(data.get('type', 'text').lower())
        
        # Process importance
        importance = ImportanceLevel(data.get('importance', 'medium').lower())
        
        # Process constraints
        constraints = None
        if 'constraints' in data:
            c_data = data['constraints']
            constraints = Constraint(
                allowed_values=c_data.get('allowed_values', []),
                min_value=c_data.get('min', None),
                max_value=c_data.get('max', None),
                max_length=c_data.get('max_length', None),
                format_regex=c_data.get('format', None),
                custom_validation=c_data.get('custom_validation', None)
            )
        
        # Process dependencies
        dependencies = []
        if 'dependencies' in data:
            for dep in data['dependencies']:
                dependencies.append(Dependency(
                    dimension=dep['dimension'],
                    rule=dep['rule']
                ))
        
        return cls(
            name=data['name'],
            description=data['description'],
            dimension_type=dim_type,
            constraints=constraints,
            importance=importance,
            dependencies=dependencies,
            examples=data.get('examples', [])
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Dimension to a dictionary.
        
        Returns:
            Dict: Dictionary representation of the Dimension
        """
        result = {
            'name': self.name,
            'description': self.description,
            'type': self.dimension_type.value,
            'importance': self.importance.value,
            'examples': self.examples
        }
        
        # Add constraints if they exist
        if self.constraints:
            constraints = {}
            if self.constraints.allowed_values:
                constraints['allowed_values'] = self.constraints.allowed_values
            if self.constraints.min_value is not None:
                constraints['min'] = self.constraints.min_value
            if self.constraints.max_value is not None:
                constraints['max'] = self.constraints.max_value
            if self.constraints.max_length is not None:
                constraints['max_length'] = self.constraints.max_length
            if self.constraints.format_regex:
                constraints['format'] = self.constraints.format_regex
            if self.constraints.custom_validation:
                constraints['custom_validation'] = self.constraints.custom_validation
            
            if constraints:
                result['constraints'] = constraints
        
        # Add dependencies if they exist
        if self.dependencies:
            result['dependencies'] = [
                {'dimension': d.dimension, 'rule': d.rule} 
                for d in self.dependencies
            ]
            
        return result


class DimensionRegistry:
    """
    Registry for managing dimensions.
    """
    def __init__(self):
        self.dimensions: Dict[str, Dimension] = {}
        
    def register(self, dimension: Dimension) -> None:
        """
        Register a dimension.
        
        Args:
            dimension: The dimension to register
        """
        self.dimensions[dimension.name] = dimension
        
    def get(self, name: str) -> Optional[Dimension]:
        """
        Get a dimension by name.
        
        Args:
            name: Name of the dimension
            
        Returns:
            Optional[Dimension]: The dimension if found, None otherwise
        """
        return self.dimensions.get(name)
        
    def list_dimensions(self) -> List[str]:
        """
        List all registered dimension names.
        
        Returns:
            List[str]: List of dimension names
        """
        return list(self.dimensions.keys())
        
    def clear(self) -> None:
        """Clear all registered dimensions."""
        self.dimensions.clear() 