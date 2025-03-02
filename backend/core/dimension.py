"""
Dimension module for the Entity Simulation Framework.

This module provides utilities for working with entity dimensions.
"""

from typing import Any, Dict, List, Optional, Union
from enum import Enum


class DimensionType(Enum):
    """Enumeration of supported dimension types."""
    BOOLEAN = "boolean"
    CATEGORICAL = "categorical"
    INT = "int"
    FLOAT = "float"
    TEXT = "text"
    
    # Legacy type for backwards compatibility
    NUMERICAL = "numerical"


def validate_dimension_config(dimension_type: str, config: Dict[str, Any]) -> bool:
    """
    Validates that a dimension configuration contains required fields for its type.
    
    Args:
        dimension_type: The type of dimension (boolean, categorical, numerical, text)
        config: Dictionary containing the dimension configuration
        
    Returns:
        True if the configuration is valid, False otherwise
    """
    if dimension_type == DimensionType.BOOLEAN.value:
        # Boolean dimensions don't require additional configuration
        return True
    
    elif dimension_type == DimensionType.CATEGORICAL.value:
        # Categorical dimensions require options list
        return isinstance(config.get('options'), list) and len(config.get('options', [])) > 0
    
    elif dimension_type == DimensionType.NUMERICAL.value:
        # Numerical dimensions require min and max values
        has_min = 'min_value' in config
        has_max = 'max_value' in config
        valid_range = True
        
        if has_min and has_max:
            valid_range = config['min_value'] < config['max_value']
            
        return has_min and has_max and valid_range
    
    elif dimension_type == DimensionType.TEXT.value:
        # Text dimensions don't require additional configuration
        return True
    
    return False


def validate_dimension_value(dimension_type: str, value: Any, config: Dict[str, Any]) -> bool:
    """
    Validates that a value is valid for a given dimension type and configuration.
    
    Args:
        dimension_type: The type of dimension (boolean, categorical, numerical, text)
        value: The value to validate
        config: Dictionary containing the dimension configuration
        
    Returns:
        True if the value is valid for the dimension, False otherwise
    """
    if dimension_type == DimensionType.BOOLEAN.value:
        return isinstance(value, bool)
    
    elif dimension_type == DimensionType.CATEGORICAL.value:
        options = config.get('options', [])
        return value in options
    
    elif dimension_type == DimensionType.NUMERICAL.value:
        if not isinstance(value, (int, float)):
            return False
        
        min_val = config.get('min_value')
        max_val = config.get('max_value')
        
        if min_val is not None and value < min_val:
            return False
        
        if max_val is not None and value > max_val:
            return False
        
        return True
    
    elif dimension_type == DimensionType.TEXT.value:
        return isinstance(value, str)
    
    return False 