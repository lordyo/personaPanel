"""
IO utilities for the GenAI Persona Framework.
Implements import/export functionality.
"""
import json
import os
import yaml
from typing import Dict, List, Optional, Any, Union

from persona_framework.modules.dimension import Dimension, DimensionRegistry
from persona_framework.modules.persona import Persona, PersonaLibrary


def load_dimensions_from_yaml(file_path: str) -> List[Dimension]:
    """
    Load dimensions from a YAML file.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        List[Dimension]: List of loaded dimensions
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dimension file not found: {file_path}")
    
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    
    dimensions = []
    for dim_data in data.get('dimensions', []):
        dimensions.append(Dimension.from_dict(dim_data))
    
    return dimensions


def save_dimensions_to_yaml(dimensions: List[Dimension], file_path: str) -> None:
    """
    Save dimensions to a YAML file.
    
    Args:
        dimensions: List of dimensions to save
        file_path: Path to the YAML file
    """
    data = {
        'dimensions': [dim.to_dict() for dim in dimensions]
    }
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)


def load_personas_from_file(file_path: str) -> PersonaLibrary:
    """
    Load personas from a file (JSON or YAML).
    
    Args:
        file_path: Path to the file
        
    Returns:
        PersonaLibrary: Library of loaded personas
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Persona file not found: {file_path}")
    
    _, ext = os.path.splitext(file_path)
    
    if ext.lower() in ['.yaml', '.yml']:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
    elif ext.lower() == '.json':
        with open(file_path, 'r') as f:
            data = json.load(f)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
    
    return PersonaLibrary.from_dict(data)


def save_personas_to_file(library: PersonaLibrary, file_path: str, format: str = 'yaml') -> None:
    """
    Save personas to a file.
    
    Args:
        library: Library of personas to save
        file_path: Path to the file
        format: Format to save in ('yaml' or 'json')
    """
    data = library.to_dict()
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    if format.lower() == 'yaml':
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    elif format.lower() == 'json':
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    else:
        raise ValueError(f"Unsupported format: {format}")


def register_dimensions_from_file(file_path: str, registry: DimensionRegistry) -> None:
    """
    Load dimensions from a file and register them.
    
    Args:
        file_path: Path to the file
        registry: Registry to register dimensions in
    """
    dimensions = load_dimensions_from_yaml(file_path)
    
    for dimension in dimensions:
        registry.register(dimension) 