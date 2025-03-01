# Entity Simulation Framework API Reference

This document provides details about the available API endpoints in the Entity Simulation Framework.

## Base URL

By default, the API is available at:

```
http://localhost:5001/api
```

## Response Format

All API responses follow this standard format:

### Success Response

```json
{
  "status": "success",
  "data": {
    // Response data here
  }
}
```

### Error Response

```json
{
  "status": "error",
  "message": "Error message here"
}
```

## Authentication

Currently, the API does not require authentication. However, an OpenAI API key must be configured in the server's environment for LLM-powered features to work.

## API Endpoints

### Health Check

Check if the API is running and properly configured.

- **URL**: `/health`
- **Method**: `GET`
- **Response Example**:
  ```json
  {
    "status": "success",
    "data": {
      "status": "ok",
      "version": "1.0.0",
      "llm_configured": true
    }
  }
  ```

### Entity Types

#### Get All Entity Types

Retrieve all entity types stored in the database.

- **URL**: `/entity-types`
- **Method**: `GET`
- **Response Example**:
  ```json
  {
    "status": "success",
    "data": [
      {
        "id": "27f4b5aa-e0ee-4cd5-9b36-e3eff05afe35",
        "name": "Human",
        "description": "A template for simulating human entities with typical personality traits and characteristics",
        "dimensions": [
          {
            "name": "age",
            "description": "The age of the human in years",
            "type": "numerical",
            "min_value": 0,
            "max_value": 120,
            "distribution": "normal"
          },
          // More dimensions...
        ],
        "created_at": "2025-03-01T12:00:00"
      }
    ]
  }
  ```

#### Get Entity Type by ID

Retrieve a specific entity type by its ID.

- **URL**: `/entity-types/:entity_type_id`
- **Method**: `GET`
- **URL Parameters**: `entity_type_id` - ID of the entity type
- **Response Example**: Same as a single object from the array above

#### Create Entity Type

Create a new entity type.

- **URL**: `/entity-types`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "name": "Custom Entity",
    "description": "A custom entity type",
    "dimensions": [
      {
        "name": "strength",
        "description": "Physical strength",
        "type": "numerical",
        "min_value": 1,
        "max_value": 10
      }
    ]
  }
  ```
- **Response Example**:
  ```json
  {
    "status": "success",
    "data": {
      "id": "a1b2c3d4-e5f6-4321-8765-1a2b3c4d5e6f"
    }
  }
  ```

### Entities

#### Create Entity

Create a new entity instance, either by providing attributes or generating them using LLM.

- **URL**: `/entities`
- **Method**: `POST`
- **Request Body (Manual)**:
  ```json
  {
    "entity_type_id": "27f4b5aa-e0ee-4cd5-9b36-e3eff05afe35",
    "name": "John Doe",
    "attributes": {
      "age": 30,
      "gender": "Male",
      "extraversion": 7
    }
  }
  ```
- **Request Body (Generated)**:
  ```json
  {
    "entity_type_id": "27f4b5aa-e0ee-4cd5-9b36-e3eff05afe35",
    "generate": true,
    "variability": "medium"
  }
  ```
- **Response Example**:
  ```json
  {
    "status": "success",
    "data": {
      "id": "f7e6d5c4-b3a2-1234-5678-9a8b7c6d5e4f"
    }
  }
  ```

#### Get Entity by ID

Retrieve a specific entity by its ID.

- **URL**: `/entities/:entity_id`
- **Method**: `GET`
- **URL Parameters**: `entity_id` - ID of the entity
- **Response Example**:
  ```json
  {
    "status": "success",
    "data": {
      "id": "f7e6d5c4-b3a2-1234-5678-9a8b7c6d5e4f",
      "entity_type_id": "27f4b5aa-e0ee-4cd5-9b36-e3eff05afe35",
      "name": "John Doe",
      "attributes": {
        "age": 30,
        "gender": "Male",
        "extraversion": 7
      },
      "created_at": "2025-03-01T12:30:00"
    }
  }
  ```

#### Get Entities by Type

Retrieve all entities of a specific type.

- **URL**: `/entity-types/:entity_type_id/entities`
- **Method**: `GET`
- **URL Parameters**: `entity_type_id` - ID of the entity type
- **Response Example**: Array of entity objects as above

### Templates

#### Get All Templates

Retrieve all predefined entity templates.

- **URL**: `/templates`
- **Method**: `GET`
- **Response Example**:
  ```json
  {
    "status": "success",
    "data": [
      {
        "id": "human",
        "name": "Human",
        "description": "A template for human entities",
        "dimension_count": 8
      }
    ]
  }
  ```

#### Get Template Details

Retrieve details of a specific template.

- **URL**: `/templates/:template_id`
- **Method**: `GET`
- **URL Parameters**: `template_id` - ID of the template
- **Response Example**:
  ```json
  {
    "status": "success",
    "data": {
      "name": "Human",
      "description": "A template for simulating human entities with typical personality traits and characteristics",
      "dimensions": [
        // Dimension objects...
      ]
    }
  }
  ```

#### Create Entity Type from Template

Create a new entity type based on a template.

- **URL**: `/templates/:template_id/create`
- **Method**: `POST`
- **URL Parameters**: `template_id` - ID of the template
- **Request Body** (optional):
  ```json
  {
    "name": "Custom Human",
    "description": "Custom human entity type"
  }
  ```
- **Response Example**:
  ```json
  {
    "status": "success",
    "data": {
      "id": "a1b2c3d4-e5f6-4321-8765-1a2b3c4d5e6f"
    }
  }
  ```

### Simulations

#### Create Simulation

Create a new simulation with entities in a context.

- **URL**: `/simulations`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "context": "A quiet coffee shop on a rainy afternoon",
    "interaction_type": "solo",
    "entity_ids": ["f7e6d5c4-b3a2-1234-5678-9a8b7c6d5e4f"],
    "metadata": {
      "tags": ["casual", "relaxed"]
    }
  }
  ```
- **Note**: `interaction_type` must be one of: "solo", "dyadic", or "group". For "solo", provide exactly 1 entity ID, for "dyadic" exactly 2, and for "group" at least 3.
- **Response Example**:
  ```json
  {
    "status": "success",
    "data": {
      "id": "1a2b3c4d-5e6f-7890-abcd-ef1234567890",
      "context_id": "abcdef12-3456-7890-abcd-ef1234567890",
      "result": "John sits by the window, watching the raindrops race down the glass. He takes a sip of his latte and pulls out a notebook, jotting down ideas for his next project. The ambient noise of the cafe helps him focus as he works through the afternoon."
    }
  }
  ```

#### Get Simulation

Retrieve a specific simulation by its ID.

- **URL**: `/simulations/:simulation_id`
- **Method**: `GET`
- **URL Parameters**: `simulation_id` - ID of the simulation
- **Response Example**:
  ```json
  {
    "status": "success",
    "data": {
      "id": "1a2b3c4d-5e6f-7890-abcd-ef1234567890",
      "timestamp": "2025-03-01T13:00:00",
      "context_id": "abcdef12-3456-7890-abcd-ef1234567890",
      "interaction_type": "solo",
      "entity_ids": ["f7e6d5c4-b3a2-1234-5678-9a8b7c6d5e4f"],
      "content": "John sits by the window...",
      "metadata": {
        "tags": ["casual", "relaxed"]
      },
      "entities": [
        // Full entity objects
      ],
      "context": {
        "id": "abcdef12-3456-7890-abcd-ef1234567890",
        "description": "A quiet coffee shop on a rainy afternoon",
        "metadata": null,
        "created_at": "2025-03-01T13:00:00"
      }
    }
  }
  ```

#### Get All Simulations

Retrieve all simulations, with optional filtering.

- **URL**: `/simulations`
- **Method**: `GET`
- **Response Example**: Array of simulation objects

## Error Codes

Common HTTP status codes returned by the API:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: LLM service not available 