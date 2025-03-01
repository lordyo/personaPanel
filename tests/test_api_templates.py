"""
Tests for the Template API endpoints.
"""

import pytest
import json
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the backend module
sys.path.append(str(Path(__file__).parent.parent))

from backend.app import app
import backend.storage as storage
from tests.db_mock import create_in_memory_db, close_test_connection, apply_db_patches, restore_db_patches

# Store the original DB_PATH for restoration
original_db_path = None

@pytest.fixture(scope="module", autouse=True)
def setup_module():
    """Set up the database patching at the module level."""
    global original_db_path
    
    # Apply patches to the storage module to use our in-memory database
    original_db_path = apply_db_patches()
    
    yield
    
    # Clean up and restore original settings
    restore_db_patches(original_db_path)

@pytest.fixture
def client():
    """Set up a test client with an in-memory database."""
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client

def test_get_templates(client):
    """Test retrieving the list of templates"""
    response = client.get('/api/templates')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['status'] == 'success'
    assert isinstance(data['data'], list)
    assert len(data['data']) >= 3  # We should have at least 3 predefined templates
    
    # Check template structure
    template = data['data'][0]
    assert 'id' in template
    assert 'name' in template
    assert 'description' in template

def test_get_template_details(client):
    """Test retrieving a specific template's details"""
    # First get the list of templates to get a valid ID
    response = client.get('/api/templates')
    templates = json.loads(response.data)['data']
    template_id = templates[0]['id']
    
    # Now request the specific template
    response = client.get(f'/api/templates/{template_id}')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['status'] == 'success'
    assert 'data' in data
    assert 'name' in data['data']
    assert 'description' in data['data']
    assert 'dimensions' in data['data']
    
    # Check dimensions structure
    dimensions = data['data']['dimensions']
    assert isinstance(dimensions, list)
    if len(dimensions) > 0:
        dimension = dimensions[0]
        assert 'name' in dimension
        assert 'type' in dimension
        # Check direct access to dimension properties (not using __dict__)
        assert isinstance(dimension['name'], str)
        assert isinstance(dimension['type'], str)

def test_nonexistent_template(client):
    """Test requesting a template that doesn't exist"""
    response = client.get('/api/templates/nonexistent_id')
    data = json.loads(response.data)
    
    assert response.status_code == 404
    assert data['status'] == 'error'

def test_create_entity_type_from_template(client):
    """Test creating an entity type from a template"""
    # First get the list of templates to get a valid ID
    response = client.get('/api/templates')
    templates = json.loads(response.data)['data']
    template_id = templates[0]['id']
    
    # Create an entity type from the template
    customization = {
        'name': 'Custom Entity Type',
        'description': 'Created from a template during testing'
    }
    
    response = client.post(
        f'/api/templates/{template_id}/create',
        data=json.dumps(customization),
        content_type='application/json'
    )
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['status'] == 'success'
    assert 'data' in data
    assert 'id' in data['data']
    assert data['data']['name'] == 'Custom Entity Type'
    assert data['data']['description'] == 'Created from a template during testing'
    assert 'dimensions' in data['data']
    
    # Verify the entity type was actually created in the database
    entity_type_id = data['data']['id']
    response = client.get(f'/api/entity-types/{entity_type_id}')
    assert response.status_code == 200 