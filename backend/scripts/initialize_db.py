#!/usr/bin/env python3
"""
Database initialization script for Entity Simulation Framework.

This script initializes the database and loads any necessary seed data.
"""

import os
import sys
import logging
from dataclasses import asdict

# Add the parent directory to sys.path to allow imports from the backend package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import storage
from core.templates import get_template_names, get_template
from core.entity import Dimension

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_database():
    """Initialize the database schema."""
    logger.info("Initializing database...")
    storage.init_db()
    logger.info("Database schema created successfully.")


def convert_dimensions_to_dicts(dimensions):
    """
    Convert Dimension objects to dictionaries for JSON serialization.
    
    Args:
        dimensions: List of Dimension objects or dictionaries
        
    Returns:
        List of dictionaries representing the dimensions
    """
    result = []
    for dim in dimensions:
        if isinstance(dim, Dimension):
            # Convert Dimension object to dict
            result.append(asdict(dim))
        elif isinstance(dim, dict):
            # Already a dict, just append
            result.append(dim)
        else:
            logger.warning(f"Unknown dimension type: {type(dim)}")
    return result


def load_templates_as_entity_types():
    """Load the predefined templates as entity types in the database."""
    logger.info("Loading templates as entity types...")
    
    try:
        template_info_list = get_template_names()
        if not template_info_list:
            logger.warning("No templates found.")
            return
            
        logger.info(f"Found {len(template_info_list)} templates")
        
        for template_info in template_info_list:
            # Extract the template ID from the dictionary
            template_id = template_info.get('id')
            if not template_id:
                logger.warning("Template info missing 'id' field. Skipping.")
                continue
                
            logger.info(f"Processing template '{template_id}'")
            
            template = get_template(template_id)
            if not template:
                logger.warning(f"Template '{template_id}' not found. Skipping.")
                continue
            
            name = template.get('name', template_id)
            description = template.get('description', f"Entity type created from template: {template_id}")
            
            # Convert Dimension objects to dictionaries
            dimensions = convert_dimensions_to_dicts(template.get('dimensions', []))
            
            # Check if this entity type already exists by name
            existing_entity_types = storage.get_all_entity_types()
            if any(et.get('name') == name for et in existing_entity_types):
                logger.info(f"Entity type '{name}' already exists. Skipping.")
                continue
            
            try:
                entity_type_id = storage.save_entity_type(name, description, dimensions)
                logger.info(f"Created entity type '{name}' with ID {entity_type_id}")
            except Exception as e:
                logger.error(f"Failed to create entity type from template '{template_id}': {e}")
                logger.exception("Detailed error:")
    except Exception as e:
        logger.error(f"Error loading templates: {e}")
        logger.exception("Stack trace:")


def main():
    """Main function to run the initialization script."""
    logger.info("Starting database initialization...")
    
    try:
        # Initialize database schema
        initialize_database()
        
        # Load predefined templates as entity types
        load_templates_as_entity_types()
        
        logger.info("Database initialization completed successfully!")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 