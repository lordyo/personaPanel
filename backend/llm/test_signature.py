#!/usr/bin/env python3
import sys
import os
import inspect
from pprint import pprint

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the create_entity_signature function
from llm.dspy_modules import create_entity_signature

def test_entity_signature():
    """
    Test function to demonstrate how create_entity_signature works
    and what the resulting signature class looks like.
    """
    # Example entity type
    entity_type = "Person"
    
    # Example entity description
    entity_description = "A professional in the tech industry with specialized knowledge and experience."
    
    # Example dimensions
    dimensions = [
        {
            "name": "age",
            "type": "numerical",
            "description": "Age in years",
            "min_value": 18,
            "max_value": 90
        },
        {
            "name": "gender",
            "type": "categorical",
            "description": "Gender identity",
            "options": ["Male", "Female", "Non-binary"]
        },
        {
            "name": "isEmployed",
            "type": "boolean",
            "description": "Whether the person is currently employed"
        },
        {
            "name": "biography",
            "type": "text",
            "description": "A short biography of the person's life and experiences"
        },
        {
            "name": "personality",
            "type": "text",
            "description": "Description of personality traits and character"
        }
    ]
    
    # Example non-text attributes
    non_text_attributes = {
        "age": 34,
        "gender": "Female",
        "isEmployed": True
    }
    
    # Variability level
    variability = "medium"
    
    # Create the signature class
    EntitySignature = create_entity_signature(
        entity_type, 
        dimensions, 
        non_text_attributes, 
        variability,
        entity_description
    )
    
    # Print signature information
    print(f"\n{'='*80}\nDSPy Signature Analysis for {entity_type}\n{'='*80}")
    
    # Print the docstring (the prompt)
    print("\nDOCSTRING (LLM PROMPT):")
    print(f"{'-'*50}")
    docstring = EntitySignature.__doc__
    if docstring:
        # Format the docstring with actual values for display
        formatted_doc = docstring.format(entity_type=entity_type, variability=variability)
        print(formatted_doc)
    else:
        print("No docstring found")
    
    # Since we can't directly inspect the instance (due to Pydantic validation),
    # extract the field definitions directly from the __init__ method source code
    init_source = inspect.getsource(EntitySignature.__init__)
    
    # Function to mock DSPy fields for display purposes
    class MockField:
        def __init__(self, name, desc, is_input):
            self.name = name
            self.desc = desc
            self.is_input = is_input
    
    # Extract the fields manually
    input_fields = []
    output_fields = []
    
    # Fixed entity_type input field
    input_fields.append(
        MockField("entity_type", f"The type of entity to create: {entity_type}", True)
    )
    
    # Entity description field
    input_fields.append(
        MockField("entity_description", f"Description of the entity: {entity_description}", True)
    )
    
    # Variability field
    input_fields.append(
        MockField("variability", f"Level of creativity in generation: {variability}", True)
    )
    
    # Dynamic input fields for non-text attributes
    for attr_name, attr_value in non_text_attributes.items():
        # Find the dimension for this attribute to get description
        dim = next((d for d in dimensions if d['name'] == attr_name), None)
        desc = f"{dim['description']}: {attr_value}" if dim else f"The {attr_name} of the entity: {attr_value}"
        input_fields.append(
            MockField(f"attr_{attr_name}", desc, True)
        )
    
    # Fixed output fields
    output_fields.append(
        MockField("name", "A unique and appropriate name for this entity", False)
    )
    output_fields.append(
        MockField("description", "A cohesive description and backstory of the entity", False)
    )
    
    # Dynamic output fields for text attributes
    for dim in dimensions:
        if dim['type'] == 'text':
            output_fields.append(
                MockField(f"text_{dim['name']}", f"{dim['description']}", False)
            )
    
    # Print input fields
    print("\nINPUT FIELDS:")
    print(f"{'-'*50}")
    if input_fields:
        for field in input_fields:
            print(f"{field.name}: {field.desc}")
    else:
        print("No input fields found")
    
    # Print output fields
    print("\nOUTPUT FIELDS:")
    print(f"{'-'*50}")
    if output_fields:
        for field in output_fields:
            print(f"{field.name}: {field.desc}")
    else:
        print("No output fields found")
    
    # Print the __init__ method source
    print("\nSIGNATURE __INIT__ METHOD:")
    print(f"{'-'*50}")
    print(init_source)
    
    # Print sample usage
    print("\nSAMPLE USAGE:")
    print(f"{'-'*50}")
    print("# Based on the signature structure, this is how it would be used:")
    print("\n# Input arguments")
    print("input_args = {")
    print(f"    \"entity_type\": \"{entity_type}\",")
    print(f"    \"entity_description\": \"{entity_description}\",")
    print(f"    \"variability\": \"{variability}\",")
    for field in input_fields:
        if field.name.startswith("attr_"):
            attr_name = field.name[5:]  # Remove 'attr_' prefix
            if attr_name in non_text_attributes:
                print(f"    \"{field.name}\": {repr(non_text_attributes[attr_name])},")
    print("}")
    
    print("\n# Make prediction")
    print("prediction = predictor(**input_args)")
    
    print("\n# Access outputs")
    for field in output_fields:
        print(f"{field.name} = prediction.{field.name}")
    
    print(f"\n{'='*80}")

if __name__ == "__main__":
    test_entity_signature() 