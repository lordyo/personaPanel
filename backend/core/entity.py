"""
Entity module for the Entity Simulation Framework.

This module defines the core classes for entity types and instances.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class Dimension:
    """
    Represents a dimension (attribute) of an entity type.
    
    Attributes:
        name: The name of the dimension
        description: A description of what this dimension represents
        type: The type of dimension (boolean, categorical, numerical, text)
        options: List of options for categorical dimensions
        min_value: Minimum value for numerical dimensions
        max_value: Maximum value for numerical dimensions
        distribution: Distribution type for numerical dimensions (e.g., "uniform", "normal")
    """
    name: str
    description: str
    type: str  # "boolean", "categorical", "numerical", "text"
    options: Optional[List[str]] = None  # For categorical
    min_value: Optional[float] = None  # For numerical
    max_value: Optional[float] = None  # For numerical
    distribution: Optional[str] = None  # For numerical


@dataclass
class EntityType:
    """
    Represents a type of entity with defined dimensions.
    
    Attributes:
        id: Unique identifier for the entity type
        name: The name of the entity type
        description: A description of what this entity type represents
        dimensions: List of dimensions that define this entity type
    """
    id: str
    name: str
    description: str
    dimensions: List[Dimension]


@dataclass
class EntityInstance:
    """
    Represents an instance of an entity with specific attribute values.
    
    Attributes:
        id: Unique identifier for the entity instance
        type_id: Reference to the entity type
        name: The name of this specific entity instance
        attributes: Dictionary of attribute values keyed by dimension name
    """
    id: str
    type_id: str
    name: str
    attributes: Dict[str, Any] 