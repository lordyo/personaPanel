# Entity Simulation System Documentation

## Overview

The PersonaPanel simulation system provides a flexible framework for simulating interactions between virtual entities. Using a streamlined architecture powered by DSPy and Large Language Models (LLMs), the system can generate realistic dialogues between any number of entities in defined contexts.

## Core Architecture

The simulation system is built around a unified approach that handles any number of entities through a single consistent interface. Key concepts include:

- **Entities**: Virtual personas with defined characteristics, personalities, and attributes
- **Context**: The situation or environment in which entities interact
- **Turns**: Individual back-and-forth dialogue exchanges within a simulation
- **Rounds**: Sequential LLM calls that build upon previous interactions

## Key Parameters

Simulations are configured using the following parameters:

- **context**: Text string that defines the environment or situation for the interaction
- **entities**: One or more entity definitions with metadata
- **n_turns**: Number of dialogue turns to generate within a single LLM call
- **simulation_rounds**: Number of sequential LLM calls that build upon previous results

## Configuration System

Simulations are configured using JSON files that separate entity definitions from simulation parameters:

### Entity Configuration File

Contains definitions of entities with their attributes:

```json
{
  "entities": [
    {
      "id": "entity-001",
      "name": "Tenzin Dorje",
      "description": "A Tibetan monk who has spent 25 years in meditation and contemplation...",
      "attributes": {
        "compassion": 0.95,
        "patience": 0.9,
        "spirituality": 0.95,
        // Other attributes
      }
    },
    // More entities...
  ]
}
```

### Simulation Configuration File

Defines the context, turns, rounds, and which entities participate:

```json
{
  "context": "A panel discussion on 'Finding Balance in Modern Life' at a wellness conference.",
  "n_turns": 3,
  "simulation_rounds": 2,
  "entity_ids": ["entity-001", "entity-002", "entity-003"]
}
```

## Directory Structure

The simulation system is organized across several directories:

- `backend/llm/interaction_module.py`: Core interaction module that powers all simulations
- `backend/simulations/`: Scripts for running simulations and tests
- `backend/simulations/config/`: Example configuration files
- `data/simulation_results/`: Simulation output and results
- `data/test_results/`: Test output files
- `data/archived_results/`: Archive of previous simulation runs
- `frontend/src/pages/`: Frontend components for simulation UI
- `frontend/src/components/`: Reusable UI components
- `frontend/src/services/`: API client services

## Technical Implementation

### InteractionSignature

The `InteractionSignature` defined in `backend/llm/interaction_module.py` specifies the input and output structure for the simulation:

```python
class InteractionSignature(dspy.Signature):
    entities: List[Dict[str, Any]] = dspy.InputField(
        desc="List of entity instances (1 to n), each with attributes including name, description and other traits"
    )
    context: str = dspy.InputField(
        desc="Detailed description of the situation or environment for the interaction"
    )
    n_turns: int = dspy.InputField(
        desc="Number of dialogue turns to generate in this call"
    )
    last_turn_number: int = dspy.InputField(
        desc="The last turn number from previous calls (default: 0, meaning start with turn 1)"
    )
    previous_interaction: Optional[str] = dspy.InputField(
        desc="Previous interaction content, if this is a continuation"
    )
    
    content: str = dspy.OutputField(
        desc="Interaction content with inner thoughts and dialogue for each entity across all turns"
    )
    final_turn_number: int = dspy.OutputField(
        desc="The number of the last turn generated in this call"
    )
```

### InteractionSimulator

The `InteractionSimulator` handles the actual simulation by interfacing with the LLM:

```python
class InteractionSimulator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(InteractionSignature)
    
    def forward(self, entities, context, n_turns=1, last_turn_number=0, previous_interaction=None):
        """Generate interactions between entities.
        
        Args:
            entities: List of entity dictionaries (can be a single entity)
            context: The situation or environment description
            n_turns: Number of dialogue turns to generate in this call
            last_turn_number: The last turn number from previous calls
            previous_interaction: Previous interaction content if continuing
            
        Returns:
            dspy.Prediction with content and final_turn_number
        """
        # Make sure entities is a list
        if not isinstance(entities, list):
            entities = [entities]
            
        result = self.predictor(
            entities=entities,
            context=context,
            n_turns=n_turns,
            last_turn_number=last_turn_number,
            previous_interaction=previous_interaction
        )
        
        return result
```

## Running Simulations

### Command-Line Interface

Simulations can be run from the command line using the `run_simulation.py` script:

```bash
python backend/simulations/run_simulation.py --config path/to/config.json --entities path/to/entities.json
```

### Simulation Tests

A comprehensive test suite covers various combinations of parameters:

```bash
cd backend/simulations
./run_simulation_tests.sh
```

## Output Format

Simulations produce JSON output that includes:

- Unique identifiers for the simulation
- Timestamp information
- Entity IDs involved in the interaction
- The simulated content with dialogue and inner thoughts
- Metadata with turn and round information

### Example Output

```
Tenzin Dorje: *I must approach this with mindfulness and compassion.*
"Perhaps we can find a middle path that honors both tradition and innovation..."

Victoria Reynolds: *He's idealistic but missing the practical realities of business.*
"While I appreciate the sentiment, in the corporate world we need measurable results..."
```

## API Integration

The simulation system includes a complete REST API for creating, retrieving, and continuing simulations through the unified simulation framework. This API allows for seamless integration with frontend applications and third-party systems.

### Unified Simulation API Endpoints

#### Create a Simulation

```
POST /api/unified-simulations
```

Creates a new simulation using the unified simulation architecture that works with any number of entities.

**Request body:**
```json
{
  "context": "Detailed description of the situation or environment",
  "entities": ["entity-id-1", "entity-id-2", "entity-id-3"],
  "n_turns": 2,
  "simulation_rounds": 1,
  "metadata": {
    "category": "politics",
    "tags": ["debate", "controversial"]
  }
}
```

**Parameters:**
- `context`: The situation or environment description
- `entities`: Array of entity IDs to include (1 or more)
- `n_turns`: Number of dialogue turns to generate in each round (default: 1)
- `simulation_rounds`: Number of sequential LLM calls to make (default: 1)
- `last_turn_number`: The last turn number for continuations (optional)
- `previous_interaction`: Previous interaction content for continuations (optional)
- `metadata`: Optional additional information

**Response:**
```json
{
  "id": "sim-20240307-1234",
  "context_id": "ctx-20240307-1234",
  "result": "TURN 1\nEntity A: *internal thoughts*\n\"Spoken dialogue\"\n...",
  "entity_count": 3,
  "final_turn_number": 2
}
```

#### Retrieve a Simulation

```
GET /api/unified-simulations/{simulation_id}
```

Retrieves a simulation by its ID.

**Response:**
```json
{
  "id": "sim-20240307-1234",
  "context": "Detailed description of the situation",
  "context_id": "ctx-20240307-1234",
  "result": "TURN 1\nEntity A: *internal thoughts*\n\"Spoken dialogue\"\n...",
  "entities": [
    {
      "id": "entity-id-1",
      "name": "Entity A",
      "description": "Description of Entity A"
    },
    ...
  ],
  "created_at": "2024-03-07T12:34:56Z",
  "metadata": { ... },
  "final_turn_number": 2
}
```

#### Continue a Simulation

```
POST /api/unified-simulations/{simulation_id}/continue
```

Continues an existing simulation with additional turns.

**Request body:**
```json
{
  "n_turns": 1,
  "simulation_rounds": 1
}
```

**Parameters:**
- `n_turns`: Number of dialogue turns to generate in each round (default: 1)
- `simulation_rounds`: Number of sequential LLM calls to make (default: 1)

**Response:**
```json
{
  "id": "sim-20240307-1234",
  "context_id": "ctx-20240307-1234",
  "result": "TURN 1\n...\nTURN 2\n...\nTURN 3\n...",
  "entity_count": 3,
  "final_turn_number": 3
}
```

#### List Simulations

```
GET /api/unified-simulations
```

Retrieves a list of simulations, with optional filtering.

**Query parameters:**
- `entity_id`: Filter by entity ID
- `entity_type_id`: Filter by entity type ID
- `limit`: Maximum number of simulations to return (default: 20)
- `offset`: Number of simulations to skip (for pagination)

**Response:**
```json
[
  {
    "id": "sim-20240307-1234",
    "context_id": "ctx-20240307-1234",
    "context": "Detailed description of the situation",
    "entity_ids": ["entity-id-1", "entity-id-2", "entity-id-3"],
    "entity_names": ["Entity A", "Entity B", "Entity C"],
    "created_at": "2024-03-07T12:34:56Z",
    "summary": "Optional summary of the simulation"
  },
  ...
]
```

## Frontend Implementation

The simulation system includes a comprehensive frontend implementation that provides an intuitive user interface for creating, viewing, and continuing simulations. The frontend components are built using modern web technologies and communicate with the backend through the unified simulation API.

### Key Frontend Components

#### SimulationList

The `SimulationList` component displays all available simulations in a card-based interface. Each card shows essential information about the simulation:

- Simulation name or ID
- Creation date
- Number of entities involved
- Current turn number
- Context snippet

Users can filter and paginate through simulations, and select individual simulations to view details or continue them.

#### SimulationCreate

The `SimulationCreate` component provides an interface for creating new simulations or continuing existing ones:

- Context definition: A text area for describing the situation
- Entity selection: A multi-select interface for choosing entities
- Parameter configuration: Settings for turns per round and simulation rounds
- Validation: Ensures that all required parameters are provided

For continuations, the component pre-fills relevant fields and ensures context consistency.

#### SimulationDetail

The `SimulationDetail` component displays the complete information about a simulation:

- Context and metadata panel
- Entity information with key attributes
- Turn-by-turn dialogue display with formatting for inner thoughts and spoken dialogue
- Continuation controls for extending simulations with additional turns

The component also provides a dialogue interface for configuring continuation parameters.

### API Integration

The frontend components integrate with the unified simulation API through a client service that handles:

- Authentication and error handling
- Data formatting and parsing
- Loading state management
- Continuation tracking

The API client abstracts the underlying HTTP requests and provides a clean interface for components to use.

### Frontend Features

- **Responsive Design**: Components adapt to different screen sizes
- **Loading States**: Provides feedback during API operations
- **Error Handling**: Displays user-friendly error messages
- **Pagination**: Supports browsing through large sets of simulations
- **Real-time Updates**: Refreshes data after operations are completed
- **Continuation Tracking**: Maintains state between simulation rounds

## Database Storage and Reliability

The simulation system uses SQLite for persistent storage of simulation data. Key implementation details:

1. **Database Schema**: The simulations table includes:
   - `id`: Unique identifier for the simulation
   - `timestamp`: Creation time
   - `context_id`: Reference to the context
   - `entity_ids`: JSON array of entity IDs
   - `content`: The simulation content
   - `metadata`: Additional info as JSON
   - `final_turn_number`: The last turn number of the simulation

2. **Final Turn Number Tracking**: 
   - Each simulation keeps track of the latest turn number through the `final_turn_number` field
   - This enables seamless continuation of simulations across multiple API calls
   - When continuing a simulation, the system retrieves this value to ensure proper sequencing

3. **Robust Error Handling**:
   - The API implements comprehensive error handling for database schema variations
   - If the `final_turn_number` column is missing (in older database versions), the system falls back to extracting the turn number from the content
   - Missing values are handled gracefully with appropriate defaults

4. **Dynamic Column Handling**:
   - The storage layer dynamically retrieves column information instead of relying on fixed indices
   - This ensures compatibility with different database schema versions
   - All database operations validate data before storage or retrieval

### Testing the API

A test script is provided at `backend/test_unified_api.sh` to validate the API functionality. To run the tests:

```bash
cd backend
./test_unified_api.sh
```

This script tests creating, retrieving, continuing, and listing simulations using the unified API. 

## Future Development

The simulation system roadmap includes:

1. **Performance Optimization**: Caching and parallel processing improvements
2. **Extended Entity Templates**: More diverse entity archetypes for varied simulations
3. **Advanced Filtering**: Enhanced search capabilities for simulations
4. **Simulation Comparisons**: Tools for comparing different simulation outcomes
5. **Analytics Dashboard**: Visual representations of simulation statistics 