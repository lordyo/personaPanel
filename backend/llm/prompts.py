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

# Entity generation prompts
ENTITY_GENERATION_PROMPT = """
You are tasked with generating a realistic and detailed entity based on the provided entity type and dimensions.

Entity Type: {entity_type}
Dimensions: {dimensions}
Variability Level: {variability}

For each dimension, generate a value that:
1. Conforms to the dimension's type (boolean, categorical, numerical, or text)
2. Stays within any constraints defined for the dimension
3. Is realistic and coherent with the entity type
4. Shows appropriate variability based on the variability level

Rules:
- Boolean dimensions should be either true or false
- Categorical dimensions should be one of the provided options
- Numerical dimensions should be within the specified range
- Text dimensions should provide concise but meaningful content

First, create a name for this entity that fits its type and nature.
Then, for each dimension, provide a value that meets the criteria above.

Your response should be structured as:

name: [Entity Name]
attributes:
  [dimension1]: [value1]
  [dimension2]: [value2]
  ...

Ensure coherence across the values so they form a believable and consistent entity.
"""

# Solo interaction simulation prompts 
SOLO_INTERACTION_PROMPT = """
You are generating a realistic response for how an entity would behave in a specific context.

ENTITY DETAILS:
Name: {entity[name]}
Attributes:
{entity_attributes}

CONTEXT:
{context}

TASK:
Generate a detailed response showing how this entity would react, feel, think, and behave in the given context. The response should:
1. Be written in third person perspective
2. Reflect the entity's characteristics and attributes
3. Provide realistic thoughts, feelings, and behaviors
4. Include dialogue if appropriate
5. Be 2-4 paragraphs in length
6. Show depth of character consistent with the entity's attributes

Write the response as a narrative describing what the entity does, thinks, and feels in this context.
"""

# Dyadic interaction simulation prompts
DYADIC_INTERACTION_PROMPT = """
You are generating a realistic dialogue and interaction between two entities in a specific context.

ENTITY 1 DETAILS:
Name: {entity1[name]}
Attributes:
{entity1_attributes}

ENTITY 2 DETAILS:
Name: {entity2[name]}
Attributes:
{entity2_attributes}

CONTEXT:
{context}

TASK:
Generate a realistic interaction between these two entities in the given context. The response should:
1. Include dialogue between the entities
2. Show how each entity's attributes influence their behavior
3. Demonstrate a realistic flow of conversation and interaction
4. Include thoughts and feelings where appropriate
5. Be 3-5 paragraphs in length
6. Have a clear beginning, middle, and conclusion to the interaction

Write the response as a narrative scene with dialogue, describing what the entities say and do.
"""

# Group interaction simulation prompts
GROUP_INTERACTION_PROMPT = """
You are generating a realistic group interaction between multiple entities in a specific context.

ENTITIES:
{entity_details}

CONTEXT:
{context}

TASK:
Generate a realistic group interaction between these entities in the given context. The response should:
1. Include dialogue between multiple entities
2. Show group dynamics and how different entities interact with each other
3. Demonstrate how each entity's attributes influence their role in the group
4. Have a clear flow to the interaction
5. Include thoughts and feelings where appropriate
6. Be 4-6 paragraphs in length

Write the response as a narrative scene with dialogue, describing what happens when these entities interact as a group.
"""

def format_entity_attributes(entity):
    """
    Format entity attributes for inclusion in a prompt.
    
    Args:
        entity: Entity dictionary with name and attributes
        
    Returns:
        Formatted string with attributes
    """
    result = []
    for key, value in entity.get('attributes', {}).items():
        result.append(f"- {key}: {value}")
    return "\n".join(result) 