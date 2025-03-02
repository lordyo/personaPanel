# Dynamic DSPy Signatures

This document explains how to dynamically create DSPy signature classes at runtime, common issues that might arise, and how to solve them.

## Overview

DSPy modules typically define static signature classes that describe the input and output fields for LLM predictions. However, there are scenarios where you need to create signature classes dynamically at runtime, such as:

- Creating entity generators with variable attributes and flexible outputs
- Building simulation modules where inputs and outputs vary based on context
- Supporting user-defined parameters and requested result fields

## The Challenge

When trying to create dynamic signatures, several challenges can arise:

1. DSPy expects signatures to be classes, not instances
2. Standard signature definitions use class inheritance and class attributes
3. Direct instantiation of `dspy.Signature` with keyword arguments doesn't work
4. Input and output fields need to be properly defined as class attributes
5. Results need to be properly extracted from varied response formats

## The Solution: Dynamic Class Creation

The solution is to use Python's metaprogramming capabilities to create a new class at runtime. Specifically, we use the `type()` function to dynamically create a subclass of `dspy.Signature`.

### Example Implementation: Dynamic Input and Output Fields

```python
def create_dynamic_signature(entity_type: str, entity_description: str, dimensions: List[Dict], output_fields: List[Dict] = None):
    """Create a dynamically constructed Signature class based on dimensions."""
    
    # Create a dictionary of attributes for the new class
    attributes = {
        "__doc__": f"""
        Generate a cohesive and believable entity based on the provided attributes.
        
        Entity Type: {entity_type}
        Description: {entity_description}
        """,
        
        # Standard input fields
        "entity_type": dspy.InputField(desc=f"The entity type: {entity_type}"),
        "entity_description": dspy.InputField(desc=f"Description of the entity type: {entity_description}"),
        "variability": dspy.InputField(desc="The level of creativity to use (0=typical, 0.5=distinct, 1=unique)"),
        
        # Standard output fields - always present
        "name": dspy.OutputField(desc="A unique and appropriate name for this entity"),
        "backstory": dspy.OutputField(desc="A cohesive description and backstory of the entity")
    }
    
    # Add dynamic input fields based on dimensions
    for dim in dimensions:
        field_name = f"dim_{dim['name']}"
        field_desc = dim.get('description', f"The {dim['name']} of this entity")
        
        # Add context based on dimension type
        if dim['type'] == 'categorical' and 'options' in dim:
            options_str = ", ".join(dim['options'])
            field_desc += f" (one of: {options_str})"
        
        # Add to attributes dictionary
        attributes[field_name] = dspy.InputField(desc=field_desc)
    
    # Add dynamic output fields if specified
    if output_fields:
        for field in output_fields:
            field_name = field.get('name', '')
            field_desc = field.get('description', f"The {field_name} of this entity")
            
            # Skip if the field is already defined (name, backstory)
            if field_name in ['name', 'backstory']:
                continue
                
            # Add output field
            attributes[field_name] = dspy.OutputField(desc=field_desc)
    
    # Create the class dynamically
    return type('DynamicEntitySignature', (dspy.Signature,), attributes)
```

### Using the Dynamic Signature

```python
# Create a dynamic signature with both input and output fields
DynamicSignature = create_dynamic_signature(
    entity_type=entity_type, 
    entity_description=entity_description, 
    dimensions=dimensions,
    output_fields=output_fields
)

# Create a predictor with this signature
predictor = dspy.Predict(DynamicSignature)

# Use the predictor
result = predictor(**input_args)
```

### Handling Dynamic Results

When working with dynamic output fields, you'll need to extract them from the result:

```python
# Create a structured result class
class EntityResult:
    def __init__(self, name, backstory, additional_fields=None):
        self.name = name
        self.backstory = backstory
        
        # Add any additional fields dynamically
        if additional_fields:
            for field_name, field_value in additional_fields.items():
                setattr(self, field_name, field_value)

# Extract values from the prediction result
name = getattr(result, 'name', None) or result.output.get('name', "Unnamed")
backstory = getattr(result, 'backstory', None) or result.output.get('backstory', "No backstory")

# Extract additional fields
additional_fields = {}
for field in output_fields:
    field_name = field['name']
    value = getattr(result, field_name, None)
    if value:
        additional_fields[field_name] = value

return EntityResult(name, backstory, additional_fields)
```

## Configuration-Driven Approach

For maximum flexibility, store entity definitions in configuration files:

```json
{
  "entity_inputs": [
    {
      "name": "Human",
      "entity_type": "Human",
      "entity_description": "A realistic human being with personality and background",
      "dimensions": [
        {
          "name": "nationality",
          "description": "The country of origin for this person",
          "type": "categorical",
          "options": ["American", "British", "Chinese"]
        }
      ],
      "output_fields": [
        {
          "name": "personality",
          "description": "The key personality traits of this person"
        },
        {
          "name": "pet",
          "description": "This person's pet, if they have one"
        }
      ]
    }
  ]
}
```

## Common Errors and Solutions

### Error: Unexpected keyword argument '__doc__'

```
TypeError: make_signature() got an unexpected keyword argument '__doc__'
```

**Problem**: Trying to instantiate a `dspy.Signature` directly with keyword arguments.

**Solution**: Use `type()` to create a new class instead:
```python
# DON'T DO THIS:
signature = dspy.Signature(__doc__="...", **fields)

# DO THIS INSTEAD:
SignatureClass = type('CustomSignature', (dspy.Signature,), {"__doc__": "...", **fields})
```

### Error: 'Prediction' object has no attribute 'name'

**Problem**: The result from the predictor doesn't have the expected attributes.

**Solution**: 
1. Debug by printing available attributes: `print(dir(result))`
2. Check if the output is in a different format (like `result.output`)
3. Create a wrapper class that handles different result formats:

```python
class EntityResult:
    def __init__(self, name, backstory, additional_fields=None):
        self.name = name
        self.backstory = backstory
        
        # Add any additional fields dynamically
        if additional_fields:
            for field_name, field_value in additional_fields.items():
                setattr(self, field_name, field_value)

# Extract values from the prediction result
name = getattr(result, 'name', None) or result.output.get('name', "Unnamed")
backstory = getattr(result, 'backstory', None) or result.output.get('backstory', "No backstory")

# Extract additional fields
additional_fields = {}
for field in output_fields:
    field_name = field['name']
    value = getattr(result, field_name, None)
    if value:
        additional_fields[field_name] = value

return EntityResult(name, backstory, additional_fields)
```

## Best Practices

1. **Always print debug information** when working with dynamic signatures:
   - Print the type of the result: `type(result).__name__`
   - Print available attributes: `dir(result)`

2. **Use a consistent naming convention**:
   - Prefix dimension fields (e.g., `dim_nationality`, `dim_age`)
   - Use clear descriptive names for output fields

3. **Handle failures gracefully**:
   - Check if attributes exist before accessing them
   - Provide fallback values for missing attributes
   - Add debug logging to help trace issues

4. **Separate standard and dynamic fields**:
   - Maintain core fields (like name, backstory) as standard in all signatures
   - Allow for flexible additional output fields based on configuration

5. **Document the expected format** of dimension and output field configurations

## Real-World Examples

The dynamic signature approach has been successfully implemented in our entity generation system. Here are some real examples of how this works:

### Human Entity with Dynamic Fields

Our system can generate a human entity with dynamic attributes and outputs:

```
Name: Amelia Thornton

Backstory:
Amelia Thornton grew up under the wide, cloudless skies of Byron Bay in Australia. As the youngest of three siblings and the only girl, she learned the art of patience early on...

Personality:
Amelia is imaginative and sensitive, marked by her keen observation skills aimed more at capturing fleeting moments than expressing herself in conversations...

Pet:
Amelia has a playful Australian Shepherd named Buddy. Similar to her spirit, Buddy has an adventurous streak...

Favorite_quote:
"Photography is a way of feeling, of touching, of loving. What you have caught on film is captured forever..."
```

### Fantasy Character with Custom Outputs

Our system also supports fantasy characters with specialized fields:

```
Name: Nyx Thornsoul

Backstory:
Once a master thief in life, Nyx Thornsoul now walks the shadowy corridors of the underworld as one of the Undead...

Abilities:
Nyx Thornsoul possesses an absolute mastery of stealth, able to meld into the despairing surroundings of night like a shadow become flesh...

Weapon:
Dual shadow-etched daggers known as "Whisper" and "Woe," adorned with cryptic runes...

Quest:
Bound to redeem his forsaken soul and end his damned un-life, Nyx seeks the three Sol Mirrors...
```

### Benefits of This Approach

1. **Extensibility**: We can easily add new entity types without code changes
2. **Configurability**: Entity attributes and outputs are defined in JSON config files
3. **Modularity**: The core DSPy module doesn't need to change for new entity types
4. **User Control**: End users can modify configurations to get different types of outputs
5. **Flexibility**: Different entity types can have completely different sets of attributes and outputs

### Multi-Entity Generation

Our system supports generating multiple entities of the same type in a single run:

```json
{
  "num_entities": 3,
  "entity_inputs": [
    /* entity definitions */
  ]
}
```

This allows you to generate groups of related entities with a single command:

```bash
python3 backend/llm/simple_entity_creator.py --entity "Human" --count 5
```

Usage examples:
- Generate a party of fantasy adventurers
- Create a group of NPCs for a game scenario
- Build a team of related business entities
- Generate multiple story characters with consistent world attributes

The multi-entity feature helps maintain consistency across related entities while still ensuring each one is unique and distinct.

### Parallel Processing

Our implementation supports parallel entity generation for improved efficiency when creating multiple entities:

```python
# Generate multiple entities in parallel with a maximum of 20 concurrent calls
python3 backend/llm/simple_entity_creator.py --entity "Human" --count 10 --max-parallel 20
```

The parallel processing implementation:
- Uses Python's `asyncio` for concurrency
- Limits concurrent API calls using a semaphore (default max: 50)
- Handles errors gracefully to ensure all entities are generated
- Maintains consistent output formatting

Performance benefits:
- Dramatically reduces total generation time for multiple entities
- Makes efficient use of available network bandwidth
- Prevents overwhelming the LLM API service
- Scales well for both small and large batches

For high-throughput scenarios, the parallel implementation can generate dozens or hundreds of entities in a fraction of the time required by sequential generation.

## Conclusion

Dynamic signature creation in DSPy is powerful but requires careful implementation. By using Python's metaprogramming capabilities, we can create flexible and extensible DSPy modules that adapt to changing requirements without sacrificing reliability.

This approach enables:
- Entity generation with variable attributes
- Customizable output fields for different entity types
- Interactive simulations with dynamic parameters
- User-configurable LLM interactions with varied result formats 