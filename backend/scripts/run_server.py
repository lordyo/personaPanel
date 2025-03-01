#!/usr/bin/env python3
"""
Run script for the Entity Simulation Framework backend server.

This script starts the Flask API server with the appropriate configuration.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the parent directory to sys.path to allow imports from the backend package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env'))


def check_environment():
    """Check if the necessary environment variables are set."""
    required_vars = ['OPENAI_API_KEY']
    missing = [var for var in required_vars if not os.environ.get(var)]
    
    if missing:
        logger.warning(f"Missing environment variables: {', '.join(missing)}")
        logger.warning("Some features may not work without these variables.")
        
        # Check specifically for OPENAI_API_KEY
        if 'OPENAI_API_KEY' in missing:
            logger.warning("OPENAI_API_KEY is missing. Simulation features will not work!")
    else:
        logger.info("All required environment variables are set.")


def main():
    """Main function to run the server."""
    logger.info("Starting Entity Simulation Framework backend server...")
    
    # Check environment
    check_environment()
    
    # Import app only after environment is configured
    from app import app
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    logger.info(f"Server starting on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true')


if __name__ == "__main__":
    main() 