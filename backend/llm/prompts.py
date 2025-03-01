"""
Prompt templates for the Entity Simulation Framework.

This module contains the prompt templates used for entity generation
and simulation with LLMs.
"""

# Entity generation prompt template
ENTITY_GENERATION_TEMPLATE = """
You are tasked with generating a realistic {entity_type} entity with the following dimensions:

{dimensions_description}

The variability level is set to: {variability}
- Low variability means creating fairly typical or average instances
- Medium variability means including some distinctive but plausible traits
- High variability means creating unique, unusual, or extreme examples

Generate a JSON object with the following structure:
{{
    "name": "Name of the entity",
    "attributes": {{
        "dimension1": value1,
        "dimension2": value2,
        ...
    }}
}}

Ensure that all attribute values conform to their dimension types and constraints.
"""

# Formatting function for dimensions description
def format_dimensions_description(dimensions):
    """
    Format a list of dimensions into a readable description for prompts.
    
    Args:
        dimensions: List of dimension dictionaries
        
    Returns:
        Formatted string describing the dimensions
    """
    descriptions = []
    
    for dim in dimensions:
        desc = f"- {dim['name']}: {dim['description']} (Type: {dim['type']})"
        
        if dim['type'] == 'categorical' and 'options' in dim:
            desc += f"\n  Options: {', '.join(dim['options'])}"
        elif dim['type'] == 'numerical':
            desc += f"\n  Range: {dim.get('min_value', 'None')} to {dim.get('max_value', 'None')}"
            if 'distribution' in dim:
                desc += f", Distribution: {dim['distribution']}"
            
        descriptions.append(desc)
    
    return "\n\n".join(descriptions)


# Solo interaction simulation prompt template
SOLO_INTERACTION_TEMPLATE = """
You are simulating how the following entity would respond in a specific context.

Entity: {entity_description}

Context: {context}

Generate a detailed, in-character response from this entity to the context.
The response should reflect the entity's characteristics and how they would
authentically behave in this situation.
"""

# Dyadic interaction simulation prompt template
DYADIC_INTERACTION_TEMPLATE = """
You are simulating an interaction between two entities in a specific context.

Entity 1: {entity1_description}

Entity 2: {entity2_description}

Context: {context}

Generate a realistic conversation between these two entities in this context.
The dialogue should reflect each entity's characteristics and how they would
authentically interact with each other in this situation.
"""

# Group interaction simulation prompt template
GROUP_INTERACTION_TEMPLATE = """
You are simulating a group interaction among multiple entities in a specific context.

Entities:
{entities_description}

Context: {context}

Generate a realistic group discussion among these entities in this context.
The discussion should reflect each entity's characteristics and how they would
authentically interact in this situation. Consider group dynamics, potential
alliances or conflicts, and how different personalities might influence the conversation.
"""

# Formatting function for entity description
def format_entity_description(entity):
    """
    Format an entity into a readable description for prompts.
    
    Args:
        entity: Entity instance dictionary
        
    Returns:
        Formatted string describing the entity
    """
    description = f"Name: {entity['name']}\n\nAttributes:"
    
    for attr_name, attr_value in entity['attributes'].items():
        description += f"\n- {attr_name}: {attr_value}"
    
    return description


# Formatting function for multiple entities
def format_entities_description(entities):
    """
    Format multiple entities into a readable description for prompts.
    
    Args:
        entities: List of entity instance dictionaries
        
    Returns:
        Formatted string describing the entities
    """
    descriptions = []
    
    for i, entity in enumerate(entities):
        descriptions.append(f"Entity {i+1}:\n{format_entity_description(entity)}")
    
    return "\n\n".join(descriptions) 