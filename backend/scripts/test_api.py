#!/usr/bin/env python3
"""
Simple API test script for the Entity Simulation Framework.

This script tests basic API endpoints to verify the backend functionality.
"""

import os
import sys
import requests
import logging
import json
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set API base URL
API_BASE_URL = "http://localhost:5001/api/"

def test_health_endpoint():
    """Test the health check endpoint."""
    logger.info("Testing health endpoint...")
    try:
        response = requests.get(urljoin(API_BASE_URL, "health"))
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"Health check response: {json.dumps(data, indent=2)}")
        
        # Verify response structure
        assert data["status"] == "success", "Unexpected status"
        assert "data" in data, "Missing data field"
        assert "status" in data["data"], "Missing status in data"
        assert data["data"]["status"] == "ok", "Health status is not ok"
        
        logger.info("Health endpoint test: PASSED")
        return True
    except Exception as e:
        logger.error(f"Health endpoint test failed: {e}")
        return False

def test_entity_types_endpoint():
    """Test retrieving all entity types."""
    logger.info("Testing entity types endpoint...")
    try:
        response = requests.get(urljoin(API_BASE_URL, "entity-types"))
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"Found {len(data['data'])} entity types")
        
        # Verify response structure
        assert data["status"] == "success", "Unexpected status"
        assert "data" in data, "Missing data field"
        assert isinstance(data["data"], list), "Data should be a list"
        
        # Print the first entity type if available
        if data["data"]:
            logger.info(f"First entity type: {json.dumps(data['data'][0], indent=2)}")
        
        logger.info("Entity types endpoint test: PASSED")
        return True
    except Exception as e:
        logger.error(f"Entity types endpoint test failed: {e}")
        return False

def test_templates_endpoint():
    """Test retrieving all templates."""
    logger.info("Testing templates endpoint...")
    try:
        response = requests.get(urljoin(API_BASE_URL, "templates"))
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"Found {len(data['data'])} templates")
        
        # Verify response structure
        assert data["status"] == "success", "Unexpected status"
        assert "data" in data, "Missing data field"
        assert isinstance(data["data"], list), "Data should be a list"
        
        # Print the first template if available
        if data["data"]:
            first_template = data["data"][0]
            logger.info(f"First template: {json.dumps(first_template, indent=2)}")
            
            # Test getting template details
            template_id = first_template["id"]
            logger.info(f"Testing template details for '{template_id}'...")
            
            detail_response = requests.get(urljoin(API_BASE_URL, f"templates/{template_id}"))
            detail_response.raise_for_status()
            detail_data = detail_response.json()
            
            assert detail_data["status"] == "success", "Unexpected status for template details"
            logger.info("Template details test: PASSED")
        
        logger.info("Templates endpoint test: PASSED")
        return True
    except Exception as e:
        logger.error(f"Templates endpoint test failed: {e}")
        return False

def main():
    """Run all API tests."""
    logger.info("Starting API tests...")
    
    # Check if server is running
    try:
        requests.get(API_BASE_URL, timeout=3)
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to API server at {API_BASE_URL}")
        logger.error("Make sure the server is running before running this test script.")
        sys.exit(1)
    
    # Run tests
    tests = [
        test_health_endpoint,
        test_entity_types_endpoint,
        test_templates_endpoint
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summarize results
    total = len(results)
    passed = sum(results)
    
    logger.info("=" * 50)
    logger.info(f"Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("All tests PASSED!")
        sys.exit(0)
    else:
        logger.error(f"{total - passed} tests FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main() 