"""
Formatting utilities for the GenAI Persona Framework.
"""
from typing import Dict, List, Any

from persona_framework.modules.persona import Persona


def format_persona_as_markdown(persona: Persona) -> str:
    """
    Format a persona as a markdown string.
    
    Args:
        persona: The persona to format
        
    Returns:
        str: Markdown representation of the persona
    """
    md = f"# {persona.name}\n\n"
    
    md += "## Traits\n\n"
    for trait in persona.traits:
        md += f"- **{trait.dimension}**: {trait.value}"
        if trait.explanation:
            md += f" _{trait.explanation}_"
        md += "\n"
    
    md += "\n## Backstory\n\n"
    md += persona.backstory + "\n\n"
    
    if persona.additional_attributes:
        md += "## Additional Attributes\n\n"
        for key, value in persona.additional_attributes.items():
            md += f"- **{key}**: {value}\n"
    
    return md


def format_personas_as_table(personas: List[Persona], dimensions: List[str] = None) -> str:
    """
    Format a list of personas as a markdown table.
    
    Args:
        personas: List of personas to format
        dimensions: List of dimensions to include (if None, include all)
        
    Returns:
        str: Markdown table representation of the personas
    """
    if not personas:
        return "No personas to display."
    
    # If dimensions not specified, use all dimensions from the first persona
    if dimensions is None:
        dimensions = list(set(trait.dimension for trait in personas[0].traits))
    
    # Create the table header
    header = "| Name | " + " | ".join(dimensions) + " |\n"
    separator = "|------|" + "|".join(["---" for _ in dimensions]) + "|\n"
    
    # Create the table rows
    rows = []
    for persona in personas:
        row = f"| {persona.name} | "
        for dim in dimensions:
            value = persona.get_trait_value(dim) or ""
            row += f"{value} | "
        rows.append(row)
    
    return header + separator + "\n".join(rows)


def format_discussion_as_markdown(discussion: str, topic: str, personas: List[Persona]) -> str:
    """
    Format a discussion as a markdown string.
    
    Args:
        discussion: The discussion text
        topic: The topic of the discussion
        personas: The personas participating in the discussion
        
    Returns:
        str: Markdown representation of the discussion
    """
    md = f"# Discussion: {topic}\n\n"
    
    md += "## Participants\n\n"
    for i, persona in enumerate(personas):
        md += f"### {i+1}. {persona.name}\n\n"
        for trait in persona.traits:
            md += f"- **{trait.dimension}**: {trait.value}\n"
        md += "\n"
    
    md += "## Discussion\n\n"
    md += discussion
    
    return md 