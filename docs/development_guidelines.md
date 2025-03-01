# Development Guidelines for Entity Simulation POC

## Directory Structure
```
entity-sim/
├── backend/
│   ├── core/                 # Core functionality
│   │   ├── entity.py         # Entity type and instance definitions
│   │   ├── dimension.py      # Dimension type definitions
│   │   └── simulation.py     # Simulation engine
│   ├── llm/                  # LLM integration
│   │   ├── dspy_modules.py   # DSPy module definitions
│   │   └── prompts.py        # Prompt templates
│   ├── storage.py            # Simple database interactions
│   └── app.py                # API server
├── frontend/
│   ├── src/                  # React application
│   │   └── App.js            # Main application
│   └── package.json          # Frontend dependencies
├── config/
│   └── default_entities.json # Default entity templates
└── README.md                 # Project documentation
```

## Coding Guidelines

### Python (Backend)
- Focus on readability and simplicity
- Include basic docstrings for main functions
- Use type hints for clarity but don't over-engineer
- Leverage LLM assistance for code generation and documentation

```python
def generate_entity(entity_type, variability="medium"):
    """Generate an entity instance based on the entity type."""
    # Implementation
    return entity
```

### JavaScript (Frontend)
- Use functional React components
- Keep components simple and focused
- Prioritize functionality over perfect architecture
- Use simple CSS for styling

```javascript
const EntityCard = ({ entity, onSelect }) => {
  return (
    <div className="entity-card" onClick={() => onSelect(entity.id)}>
      <h3>{entity.name}</h3>
      {/* Display entity attributes */}
    </div>
  );
};
```

## DSPy Implementation

### Module Approach
- Create clear, focused DSPy modules for specific tasks
- Use simple prompts that can be refined later
- Prioritize getting a working solution over perfect design

```python
import dspy

# Configure LLM
lm = dspy.LM('openai/gpt-4o-mini')
dspy.configure(lm=lm)

class EntityGenerator(dspy.Module):
    """Generate entity instances based on entity type definition."""
    
    def __init__(self):
        self.generate = dspy.ChainOfThought(
            "entity_type, dimensions, variability -> name, attributes"
        )
    
    def forward(self, entity_type, dimensions, variability="medium"):
        result = self.generate(
            entity_type=entity_type,
            dimensions=dimensions,
            variability=variability
        )
        return result
```

## Database Approach

### Database Schema
- Use SQLite for simplicity (file-based, no server required)
- Keep the schema simple with minimal tables
- Use basic SQL queries without an ORM to start

```python
import sqlite3
import json
import uuid

def init_db():
    """Initialize the database with basic tables."""
    conn = sqlite3.connect('entity_sim.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entity_types (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        dimensions TEXT NOT NULL  -- JSON string
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entities (
        id TEXT PRIMARY KEY,
        entity_type_id TEXT NOT NULL,
        name TEXT NOT NULL,
        attributes TEXT NOT NULL,  -- JSON string
        FOREIGN KEY (entity_type_id) REFERENCES entity_types (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS simulations (
        id TEXT PRIMARY KEY,
        context TEXT NOT NULL,
        entities TEXT NOT NULL,  -- JSON array of entity IDs
        result TEXT             -- JSON string
    )
    ''')
    
    conn.commit()
    conn.close()

def save_entity_type(name, description, dimensions):
    """Save an entity type to the database."""
    conn = sqlite3.connect('entity_sim.db')
    cursor = conn.cursor()
    
    entity_type_id = str(uuid.uuid4())
    cursor.execute(
        'INSERT INTO entity_types VALUES (?, ?, ?, ?)',
        (entity_type_id, name, description, json.dumps(dimensions))
    )
    
    conn.commit()
    conn.close()
    return entity_type_id
```

## API Implementation

### Flask Implementation
- Use Flask for a lightweight API
- Implement only the necessary endpoints
- Keep request/response formats simple

```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

@app.route('/api/entity-types', methods=['GET'])
def get_entity_types():
    # Implementation
    return jsonify(entity_types)

@app.route('/api/generate-entities', methods=['POST'])
def generate_entities():
    data = request.json
    entity_type_id = data['entityTypeId']
    count = data.get('count', 1)
    variability = data.get('variability', 'medium')
    
    # Implementation
    
    return jsonify(entities)

if __name__ == '__main__':
    app.run(debug=True)
```

## Testing Approach

### Focus on Manual Testing
- Prioritize manual testing over automated tests for the POC
- Test core functionality through the UI
- Use print statements and logging for debugging
- Consider simple smoke tests for critical functions

```python
def smoke_test_entity_generation():
    """Simple smoke test for entity generation."""
    # Create a simple entity type
    human_type = {
        "name": "Human",
        "dimensions": [
            {"name": "age", "type": "numerical", "min": 18, "max": 80},
            {"name": "gender", "type": "categorical", "options": ["male", "female", "non-binary"]}
        ]
    }
    
    # Generate an entity
    generator = EntityGenerator()
    entity = generator.forward(
        entity_type=human_type["name"],
        dimensions=human_type["dimensions"]
    )
    
    print("Generated entity:", entity)
    
    # Simple validation
    assert "name" in entity
    assert "attributes" in entity
    assert "age" in entity.attributes
    assert "gender" in entity.attributes
```

## Error Handling

### Error Handling Approach
- Focus on catching and logging errors for debugging
- Use try/except blocks for critical operations
- Include basic user feedback for errors
- Keep error messages informative but simple

```python
def generate_entities(entity_type_id, count, variability):
    """Generate entities with error handling."""
    try:
        # Implementation
        return entities
    except Exception as e:
        print(f"Error generating entities: {e}")
        return {"error": "Failed to generate entities", "details": str(e)}
```

## Development Workflow

### Development Process
1. Start with backend core functionality
2. Implement simple API endpoints
3. Create a basic frontend with essential UI components
4. Iterate on features in small increments
5. Use LLM assistance for code generation and problem-solving
6. Manually test each feature as you implement it

## Documentation

### Documentation Approach
- Focus on README with setup instructions and basic usage
- Include inline comments for complex logic
- Document API endpoints with examples
- Maintain a simple development log to track progress

## Deployment for Testing

### Local Development
1. Run backend Flask server locally
2. Serve React frontend using Create React App's development server
3. Store data in local SQLite database
4. Use environment variables for API keys

## Time-Saving Tips

### Leverage LLM Support
- Use Claude or other LLMs to generate boilerplate code
- Ask for help with debugging complex issues
- Request sample implementations for challenging features
- Use LLMs to create initial prompts for DSPy modules

### Focus on Core Functionality First
1. Entity type definition and storage
2. Entity generation with LLM
3. Basic simulation (solo interactions)
4. Simple UI for managing the workflow
5. Result display and basic export

### Prototype Before Polishing
- Get a working end-to-end system before refining
- Use simple JSON files for initial data storage if needed
- Focus on functional UI before aesthetics
- Implement basic error handling and improve later