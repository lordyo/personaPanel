"""
Dynamic DSPy Signature Creator for Entity Generation.

This module provides utilities for creating dynamic DSPy signature classes at runtime,
which is essential for entity generation with variable attributes.
"""

import dspy
from typing import Dict, List, Any, Optional

def create_dynamic_signature(entity_type: str, 
                           entity_description: str, 
                           dimensions: List[Dict], 
                           non_text_attributes: Dict[str, Any] = None,
                           variability: str = "medium",
                           output_fields: List[Dict] = None):
    """
    Create a dynamically constructed DSPy Signature class based on entity dimensions.
    
    Args:
        entity_type: The type of entity to generate
        entity_description: Description of the entity type
        dimensions: List of dimension dictionaries defining the entity attributes
        non_text_attributes: Dictionary of pre-generated non-text attributes
        variability: Level of variability in generation ("low", "medium", "high")
        output_fields: List of additional output fields to generate (optional)
        
    Returns:
        A DSPy Signature class with properly defined input and output fields
    """
    # Create a new Signature class dynamically using type()
    attributes = {
        "__doc__": f"""
        Generate a cohesive and believable {entity_type} entity based on the provided attributes.
        
        Entity Type: {entity_type}
        Description: {entity_description}
        Variability: {variability} (use this to determine how conventional or unique the entity should be)
        """,
        
        # Standard input fields
        "entity_type": dspy.InputField(desc=f"The entity type: {entity_type}"),
        "entity_description": dspy.InputField(desc=f"Description of the entity type: {entity_description}"),
        "variability": dspy.InputField(desc="The level of creativity to use (low=typical, medium=distinct, high=unique)"),
        
        # Standard output fields - always present
        "name": dspy.OutputField(desc="A unique and appropriate name for this entity"),
        "description": dspy.OutputField(desc="A cohesive description and backstory of the entity that incorporates all the provided attributes")
    }
    
    # Add non-text attributes as input fields
    if non_text_attributes:
        for attr_name, attr_value in non_text_attributes.items():
            # Find the dimension for this attribute to get description
            dim = next((d for d in dimensions if d['name'] == attr_name), None)
            desc = f"{dim['description'] if dim else attr_name}: {attr_value}"
            
            # Add input field with formatted description
            attributes[f"attr_{attr_name}"] = dspy.InputField(desc=desc)
    
    # Add dynamic output fields for text attributes
    for dim in dimensions:
        if dim['type'] == 'text':
            field_name = f"text_{dim['name']}"
            field_desc = dim.get('description', f"The {dim['name']} of this entity")
            attributes[field_name] = dspy.OutputField(desc=field_desc)
    
    # Add additional custom output fields if specified
    if output_fields:
        for field in output_fields:
            field_name = field.get('name', '')
            field_desc = field.get('description', f"The {field_name} of this entity")
            
            # Skip if the field is already defined
            if field_name in ['name', 'description'] or f"text_{field_name}" in attributes:
                continue
                
            # Add output field
            attributes[field_name] = dspy.OutputField(desc=field_desc)
    
    # Create the class dynamically using type()
    return type('DynamicEntitySignature', (dspy.Signature,), attributes)


class EntityResult:
    """
    Structured result class for entity generation.
    
    This class provides a standardized way to extract and store entity generation results,
    handling different possible result formats from DSPy predictions.
    """
    
    def __init__(self, name=None, description=None, attributes=None, additional_fields=None):
        """
        Initialize the entity result with extracted values.
        
        Args:
            name: The entity's name
            description: The entity's description/backstory
            attributes: Dictionary of attribute values
            additional_fields: Dictionary of additional field values
        """
        self.name = name or "Unnamed Entity"
        self.description = description or "No description available"
        self.attributes = attributes or {}
        
        # Add any additional fields as attributes
        if additional_fields:
            for field_name, field_value in additional_fields.items():
                setattr(self, field_name, field_value)
                
    @classmethod
    def from_prediction(cls, prediction, dimensions, non_text_attributes=None, output_fields=None):
        """
        Extract entity information from a DSPy prediction result.
        
        Args:
            prediction: The DSPy prediction object
            dimensions: List of dimension dictionaries
            non_text_attributes: Dictionary of non-text attribute values
            output_fields: List of additional output fields
            
        Returns:
            An EntityResult instance with extracted values
        """
        # Debug the prediction object
        print(f"\nPrediction type: {type(prediction).__name__}")
        print(f"Available attributes: {dir(prediction)}")
        
        # Initialize result values
        name = None
        description = None
        attributes = non_text_attributes.copy() if non_text_attributes else {}
        additional_fields = {}
        
        # Extract name - try different possible locations
        if hasattr(prediction, 'name'):
            name = prediction.name
        elif hasattr(prediction, 'output') and isinstance(prediction.output, dict) and 'name' in prediction.output:
            name = prediction.output['name']
        
        # Extract description - try different possible locations
        if hasattr(prediction, 'description'):
            description = prediction.description
        elif hasattr(prediction, 'output') and isinstance(prediction.output, dict) and 'description' in prediction.output:
            description = prediction.output['description']
        
        # Extract text attributes from dimensions
        for dim in dimensions:
            if dim['type'] == 'text':
                field_name = f"text_{dim['name']}"
                # Try to get the value from the prediction
                if hasattr(prediction, field_name):
                    attributes[dim['name']] = getattr(prediction, field_name)
                elif hasattr(prediction, 'output') and isinstance(prediction.output, dict) and field_name in prediction.output:
                    attributes[dim['name']] = prediction.output[field_name]
        
        # Extract additional output fields
        if output_fields:
            for field in output_fields:
                field_name = field.get('name')
                if hasattr(prediction, field_name):
                    additional_fields[field_name] = getattr(prediction, field_name)
                elif hasattr(prediction, 'output') and isinstance(prediction.output, dict) and field_name in prediction.output:
                    additional_fields[field_name] = prediction.output[field_name]
        
        return cls(name, description, attributes, additional_fields) 