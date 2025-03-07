"""
Entity module for the Entity Simulation Framework.

This module defines the core classes for entity types and instances.
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class Dimension:
    """
    Represents a dimension (attribute) of an entity type.
    
    Attributes:
        name: The name of the dimension
        description: A description of what this dimension represents
        type: The type of dimension (boolean, categorical, int, float, text)
        options: List of options for categorical dimensions
        min_value: Minimum value for int/float dimensions
        max_value: Maximum value for int/float dimensions
        distribution: Distribution type for int/float dimensions (uniform, normal, skewed)
                     or percentage for boolean
        true_percentage: Percentage chance of true for boolean dimensions (default 0.5)
        std_deviation: Standard deviation for normal distribution (legacy)
        spread_factor: Controls the spread of values for normal distribution (0-1)
        skew_factor: Skew factor for skewed distribution (-5 to 5)
        distribution_values: Distribution percentages for categorical options
    """
    name: str
    description: str
    type: str  # "boolean", "categorical", "int", "float", "text"
    options: Optional[List[str]] = None  # For categorical
    min_value: Optional[Union[int, float]] = None  # For int/float
    max_value: Optional[Union[int, float]] = None  # For int/float
    distribution: Optional[str] = None  # For int/float: "uniform", "normal", "skewed", For boolean: "percentage"
    true_percentage: Optional[float] = None  # For boolean, default 0.5
    std_deviation: Optional[float] = None  # For normal distribution (legacy)
    spread_factor: Optional[float] = None  # For normal distribution (0-1, controls spread)
    skew_factor: Optional[float] = None  # For skewed distribution
    distribution_values: Optional[Dict[str, float]] = None  # For categorical


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