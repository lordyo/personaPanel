# GenAI Persona Framework - Technical Documentation

## Overview

The GenAI Persona Framework is a DSPy-based system for generating and utilizing AI personas. This implementation uses FastAPI for the backend, React for the frontend, and JSON Server for persistence. The system generates diverse, coherent personas with customizable traits using Claude 3 Sonnet via DSPy for enhanced generation quality.

## Architecture

### Current Implementation

The current implementation consists of three main components:

1. **FastAPI Backend (port 8000)**
   - Handles persona generation using DSPy and Claude
   - Exposes API endpoints for persona generation and management
   - Manages dimension definitions

2. **React Frontend (port 3000)**
   - User interface for generating and managing personas
   - Allows configuration of generation parameters
   - Provides visualization and editing of personas

3. **JSON Server (port 5000)**
   - Provides persistence for personas and dimensions
   - Serves as a simple database substitute

### Core Components

1. **Dimension System**
   - Defines the attributes that make up a persona
   - Supports different types (categorical, numeric, text)
   - Managed via the DimensionRegistry class

2. **Persona System**
   - Represents a coherent collection of traits
   - Includes name, traits, backstory, and additional attributes
   - Managed via the PersonaLibrary class

3. **Generation Pipeline**
   - Uses DSPy's ChainOfThought with Claude to create personas
   - Supports diversity controls through the diversity_level parameter
   - Ensures generated personas have all required attributes

4. **API Layer**
   - FastAPI endpoints for persona generation and management
   - CORS support for cross-origin requests
   - Error handling and validation

### Class Hierarchy

```
persona_framework/
├── modules/
│   ├── dimension.py
│   │   ├── Dimension
│   │   ├── DimensionType
│   │   ├── ImportanceLevel
│   │   └── DimensionRegistry
│   ├── persona.py
│   │   ├── Trait
│   │   ├── Persona
│   │   └── PersonaLibrary
│   ├── generator.py
│   │   ├── PersonaGenerationSignature
│   │   ├── PersonaGenerator
│   │   └── PersonaGeneratorWithValidation
│   └── validator.py
│       ├── PersonaValidator
│       └── ValidationResult
├── utils/
│   ├── formatting.py
│   ├── io.py
│   └── sampling.py
```

### Application Structure

```
/
├── backend_server.py        # FastAPI server implementation
├── persona_framework/       # Core framework implementation
├── frontend/                # React frontend application
│   └── persona-panel/       # React application root
├── project_docs/            # Documentation
└── requirements.txt         # Python dependencies
```

## Key Classes and Interfaces

### Dimension System

#### `Dimension`
Represents a single dimension of a persona.

```python
@dataclass
class Dimension:
    name: str
    description: str
    type: DimensionType
    importance: ImportanceLevel
    constraints: Optional[Dict[str, Any]] = None
    examples: Optional[List[Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        # Converts to dictionary for serialization
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Dimension':
        # Creates a Dimension from a dictionary
```

#### `DimensionRegistry`
Manages a collection of dimensions.

```python
class DimensionRegistry:
    def __init__(self):
        self.dimensions = {}
    
    def register(self, dimension: Dimension) -> None:
        # Registers a dimension
        
    def get(self, name: str) -> Optional[Dimension]:
        # Retrieves a dimension by name
        
    def list_dimensions(self) -> List[str]:
        # Lists all registered dimensions
        
    def clear(self) -> None:
        # Clears all registered dimensions
```

### Persona System

#### `Trait`
Represents a specific value for a dimension.

```python
@dataclass
class Trait:
    dimension: str
    value: Any
    explanation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        # Converts to dictionary for serialization
```

#### `Persona`
Represents a complete persona with traits and backstory.

```python
@dataclass
class Persona:
    id: str
    name: str
    traits: List[Trait]
    backstory: str
    additional_attributes: Optional[Dict[str, Any]] = None
    
    def get_trait(self, dimension: str) -> Optional[Trait]:
        # Gets a trait by dimension name
        
    def to_dict(self) -> Dict[str, Any]:
        # Converts to dictionary for serialization
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Persona':
        # Creates a Persona from a dictionary
```

#### `PersonaLibrary`
Manages a collection of personas.

```python
class PersonaLibrary:
    def __init__(self):
        self.personas = {}
    
    def add(self, persona: Persona) -> None:
        # Adds a persona to the library
        
    def get(self, id: str) -> Optional[Persona]:
        # Retrieves a persona by ID
        
    def list_personas(self) -> List[Persona]:
        # Lists all personas
        
    def clear(self) -> None:
        # Clears all personas
```

### Generation System

#### `PersonaGenerationSignature`
DSPy signature for persona generation.

```python
class PersonaGenerationSignature(dspy.Signature):
    dimensions = dspy.InputField(desc="List of dimension definitions")
    num_personas = dspy.InputField(desc="Number of personas to generate")
    diversity_level = dspy.InputField(desc="Required diversity between personas (low/medium/high)")
    personas = dspy.OutputField(desc="List of generated personas with names, traits and backstories")
```

#### `PersonaGenerator`
Generates personas based on dimension definitions.

```python
class PersonaGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_personas = dspy.ChainOfThought(PersonaGenerationSignature)
    
    def forward(self, dimensions: List[Dict], num_personas: int, diversity_level: str = "medium") -> List[Dict]:
        # Generates personas using DSPy
```

#### `PersonaGeneratorWithValidation`
Extends `PersonaGenerator` with validation.

```python
class PersonaGeneratorWithValidation:
    def __init__(self, dimension_registry: DimensionRegistry):
        self.dimension_registry = dimension_registry
        self.generator = PersonaGenerator()
        self.validator = PersonaValidator(dimension_registry)
    
    def generate(self, num_personas: int, diversity_level: str = "medium") -> List[Persona]:
        # Generates and validates personas
```

## API Endpoints

### FastAPI Backend (port 8000)

```
GET /                           - Root endpoint (health check)
GET /api/stats                  - Get statistics (persona and dimension counts)
GET /api/dimensions             - Get all registered dimensions
POST /api/personas/generate     - Generate personas with specified settings
POST /api/personas/save         - Save a persona to the library
GET /api/personas               - Get all personas from the library
```

### JSON Server (port 5000)

```
GET /dimensions                 - Get all dimensions
POST /dimensions                - Create a new dimension
PUT /dimensions/:id             - Update a dimension
DELETE /dimensions/:id          - Delete a dimension
GET /personas                   - Get all personas
POST /personas                  - Create a new persona
PUT /personas/:id               - Update a persona
DELETE /personas/:id            - Delete a persona
```

## Known Issues and Solutions

### 1. Dashboard Statistics
**Issue**: Dashboard shows 0 Personas and 0 Dimensions despite having both.

**Solution**: The backend API is not properly tracking personas and dimensions in the in-memory persona_library and dimension_registry. Need to implement proper synchronization between the API state and the JSON server.

### 2. Persona Saving
**Issue**: "Failed to create persona" error when saving.

**Solution**: The frontend is making requests to JSON Server (`http://localhost:5000/personas`) but our backend implementation at `http://localhost:8000/api/personas/save` is expecting a different request format. Need to align the frontend API service with the backend API endpoints.

### 3. Same Persona Generation
**Issue**: Regenerating with same parameters yields identical personas.

**Solution**: The DSPy generation needs randomization through a temperature parameter or random seed for each generation request. Modify the generator.py to add randomness to each generation.

### 4. Settings Reset on Navigation
**Issue**: Settings reset when navigating between pages.

**Solution**: Implement frontend state persistence using localStorage or React context to maintain settings across navigation.

### 5. Backend Python Environment Issues
**Issue**: Errors running backend with system Python due to environment conflicts.

**Solution**: Use a dedicated virtual environment with all dependencies installed:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python backend_server.py
```

## Development Workflow

### Starting the Application

1. **Start the Backend**:
   ```bash
   source venv/bin/activate
   python backend_server.py
   ```
   This starts the FastAPI server on port 8000.

2. **Start the JSON Server**:
   ```bash
   cd frontend/persona-panel
   npx json-server --watch db.json --port 5000
   ```
   This starts the JSON Server on port 5000.

3. **Start the Frontend**:
   ```bash
   cd frontend/persona-panel
   npm start
   ```
   This starts the React application on port 3000.

### Using the Application

1. Visit http://localhost:3000 to access the application
2. Generate personas by configuring dimensions and diversity settings
3. Save and manage personas through the interface
4. View statistics on the dashboard

## Best Practices

### Dimension Design
- Keep dimensions orthogonal when possible
- Use clear, descriptive names
- Define constraints carefully
- Test generation with different combinations of dimensions

### Persona Generation
- Start with a small number of dimensions for faster generation
- Balance diversity level based on the use case
- Generate personas with different combinations of dimensions to test flexibility
- Save successful personas for future use

### Error Handling
- Check backend logs for detailed error information
- Ensure environment variables (especially API keys) are properly set
- Validate API requests and responses
- Handle edge cases (empty dimensions, invalid requests)

## Future Improvements

1. **Enhanced Persistence**: Replace JSON Server with a proper database
2. **Improved Error Handling**: Add more detailed error reporting
3. **User Authentication**: Add user accounts and authentication
4. **Batch Operations**: Support for batch generation and management
5. **State Management**: Implement Redux or Context API for better state management
6. **Caching**: Add caching for expensive operations
7. **Testing**: Add comprehensive unit and integration tests

## Conclusion

The GenAI Persona Framework provides a flexible system for generating and utilizing AI personas using DSPy and Claude. The current implementation demonstrates the core functionality but requires some fixes to address the identified issues. Following the solutions provided in this document should resolve the current limitations and improve the overall user experience.
