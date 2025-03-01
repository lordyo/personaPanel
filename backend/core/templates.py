"""
Entity Templates module for the Entity Simulation Framework.

This module defines predefined entity templates that users can select as a starting point.
"""

from typing import List, Dict, Any
from .entity import Dimension

# Predefined Entity Templates
ENTITY_TEMPLATES = {
    "human": {
        "name": "Human",
        "description": "A template for simulating human entities with typical personality traits and characteristics",
        "dimensions": [
            Dimension(
                name="age",
                description="The age of the human in years",
                type="numerical",
                min_value=0,
                max_value=120,
                distribution="normal"
            ),
            Dimension(
                name="gender",
                description="The gender identity of the human",
                type="categorical",
                options=["Male", "Female", "Non-binary", "Other"]
            ),
            Dimension(
                name="extraversion",
                description="The degree to which the person is outgoing and social (1-10 scale)",
                type="numerical",
                min_value=1,
                max_value=10,
                distribution="uniform"
            ),
            Dimension(
                name="agreeableness",
                description="The degree to which the person is warm and cooperative (1-10 scale)",
                type="numerical",
                min_value=1, 
                max_value=10,
                distribution="uniform"
            ),
            Dimension(
                name="conscientiousness",
                description="The degree to which the person is organized and responsible (1-10 scale)",
                type="numerical",
                min_value=1,
                max_value=10,
                distribution="uniform"
            ),
            Dimension(
                name="neuroticism",
                description="The degree to which the person experiences negative emotions (1-10 scale)",
                type="numerical",
                min_value=1,
                max_value=10,
                distribution="uniform"
            ),
            Dimension(
                name="openness",
                description="The degree to which the person is curious and creative (1-10 scale)",
                type="numerical",
                min_value=1,
                max_value=10,
                distribution="uniform"
            ),
            Dimension(
                name="background",
                description="Brief background information about the person's history",
                type="text"
            ),
            Dimension(
                name="is_employed",
                description="Whether the person is currently employed",
                type="boolean"
            )
        ]
    },
    
    "fantasy_character": {
        "name": "Fantasy Character",
        "description": "A template for creating characters in a fantasy setting with magical abilities and traits",
        "dimensions": [
            Dimension(
                name="race",
                description="The fantasy race of the character",
                type="categorical",
                options=["Human", "Elf", "Dwarf", "Orc", "Halfling", "Gnome", "Dragon-born", "Other"]
            ),
            Dimension(
                name="class",
                description="The character's role or profession",
                type="categorical",
                options=["Warrior", "Mage", "Rogue", "Cleric", "Bard", "Ranger", "Paladin", "Warlock", "Druid"]
            ),
            Dimension(
                name="age",
                description="The age of the character in years",
                type="numerical",
                min_value=16,
                max_value=1000,
                distribution="uniform"
            ),
            Dimension(
                name="strength",
                description="Physical power (1-20 scale)",
                type="numerical",
                min_value=1,
                max_value=20,
                distribution="normal"
            ),
            Dimension(
                name="dexterity",
                description="Agility and reflexes (1-20 scale)",
                type="numerical",
                min_value=1,
                max_value=20,
                distribution="normal"
            ),
            Dimension(
                name="constitution",
                description="Endurance and vitality (1-20 scale)",
                type="numerical",
                min_value=1,
                max_value=20,
                distribution="normal"
            ),
            Dimension(
                name="intelligence",
                description="Reasoning and memory (1-20 scale)",
                type="numerical",
                min_value=1,
                max_value=20,
                distribution="normal"
            ),
            Dimension(
                name="wisdom",
                description="Perception and insight (1-20 scale)",
                type="numerical",
                min_value=1,
                max_value=20,
                distribution="normal"
            ),
            Dimension(
                name="charisma",
                description="Force of personality (1-20 scale)",
                type="numerical",
                min_value=1,
                max_value=20,
                distribution="normal"
            ),
            Dimension(
                name="backstory",
                description="The character's origin story and motivations",
                type="text"
            ),
            Dimension(
                name="has_magic",
                description="Whether the character can use magic",
                type="boolean"
            )
        ]
    },
    
    "organization": {
        "name": "Organization",
        "description": "A template for creating and simulating organizations like companies, governments, or groups",
        "dimensions": [
            Dimension(
                name="type",
                description="The type of organization",
                type="categorical",
                options=["Corporation", "Government", "Non-profit", "Educational", "Religious", "Criminal", "Military"]
            ),
            Dimension(
                name="size",
                description="Number of members/employees",
                type="numerical",
                min_value=1,
                max_value=1000000,
                distribution="exponential"
            ),
            Dimension(
                name="founding_year",
                description="Year the organization was founded",
                type="numerical",
                min_value=1700,
                max_value=2023,
                distribution="uniform"
            ),
            Dimension(
                name="influence",
                description="The organization's influence on society (1-10 scale)",
                type="numerical",
                min_value=1,
                max_value=10,
                distribution="normal"
            ),
            Dimension(
                name="wealth",
                description="The financial resources of the organization (1-10 scale)",
                type="numerical",
                min_value=1,
                max_value=10,
                distribution="exponential"
            ),
            Dimension(
                name="corruption",
                description="The level of corruption within the organization (1-10 scale)",
                type="numerical",
                min_value=1,
                max_value=10,
                distribution="normal"
            ),
            Dimension(
                name="ideology",
                description="The guiding principles or beliefs of the organization",
                type="text"
            ),
            Dimension(
                name="leadership_structure",
                description="How the organization is led and decisions are made",
                type="categorical",
                options=["Autocratic", "Democratic", "Oligarchic", "Meritocratic", "Anarchic", "Bureaucratic"]
            ),
            Dimension(
                name="publicly_traded",
                description="Whether the organization is publicly traded on stock markets",
                type="boolean"
            ),
            Dimension(
                name="description",
                description="General description and notable information about the organization",
                type="text"
            )
        ]
    }
}

def get_template_names() -> List[Dict[str, str]]:
    """
    Returns a list of available templates with their names and descriptions.
    
    Returns:
        List of dictionaries with template id, name, and description
    """
    return [
        {
            "id": template_id,
            "name": template_info["name"],
            "description": template_info["description"]
        }
        for template_id, template_info in ENTITY_TEMPLATES.items()
    ]

def get_template(template_id: str) -> Dict[str, Any]:
    """
    Returns the template with the given ID.
    
    Args:
        template_id: The ID of the template to retrieve
        
    Returns:
        The template dictionary or None if not found
    """
    return ENTITY_TEMPLATES.get(template_id) 