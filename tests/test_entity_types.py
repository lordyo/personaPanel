"""
Tests for the Entity Type API endpoints.
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

def test_get_entity_types_empty(client):
    """Test retrieving entity types when none exist"""
    response = client.get('/api/entity-types')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 0

def test_create_entity_type(client):
    """Test creating a new entity type"""
    entity_type = {
        'name': 'Test Entity Type',
        'description': 'A test entity type',
        'dimensions': [
            {
                'name': 'test_bool',
                'description': 'A boolean test dimension',
                'type': 'boolean'
            },
            {
                'name': 'test_num',
                'description': 'A numerical test dimension',
                'type': 'numerical',
                'min_value': 1,
                'max_value': 10,
                'distribution': 'uniform'
            },
            {
                'name': 'test_cat',
                'description': 'A categorical test dimension',
                'type': 'categorical',
                'options': ['Option 1', 'Option 2', 'Option 3']
            }
        ]
    }
    
    response = client.post(
        '/api/entity-types',
        data=json.dumps(entity_type),
        content_type='application/json'
    )
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert 'id' in data
    
    # Verify the entity type was created
    entity_type_id = data['id']
    response = client.get(f'/api/entity-types/{entity_type_id}')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['name'] == 'Test Entity Type'
    assert data['description'] == 'A test entity type'
    assert len(data['dimensions']) == 3
    
    # Check if we can now get the list of entity types
    response = client.get('/api/entity-types')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['name'] == 'Test Entity Type'

def test_validation_errors(client):
    """Test validation errors when creating an entity type"""
    # Test missing name
    entity_type = {
        'description': 'Missing name',
        'dimensions': [
            {
                'name': 'test_dim',
                'description': 'A test dimension',
                'type': 'boolean'
            }
        ]
    }
    
    response = client.post(
        '/api/entity-types',
        data=json.dumps(entity_type),
        content_type='application/json'
    )
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert 'error' in data
    assert 'Name is required' in data['error']
    
    # Test missing dimensions
    entity_type = {
        'name': 'No Dimensions',
        'description': 'Entity type with no dimensions'
    }
    
    response = client.post(
        '/api/entity-types',
        data=json.dumps(entity_type),
        content_type='application/json'
    )
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert 'error' in data
    assert 'At least one dimension is required' in data['error']

def test_get_nonexistent_entity_type(client):
    """Test requesting an entity type that doesn't exist"""
    response = client.get('/api/entity-types/nonexistent_id')
    data = json.loads(response.data)
    
    assert response.status_code == 404
    assert 'error' in data
    