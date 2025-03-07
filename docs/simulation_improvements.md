# Entity Simulation System Documentation

## Overview

The PersonaPanel simulation system provides a flexible framework for simulating interactions between virtual entities. Using a streamlined architecture powered by DSPy and Large Language Models (LLMs), the system can generate realistic dialogues between one or more entities in defined contexts.

## Core Architecture

The simulation system is built around a unified approach that handles any number of entities (solo, dyadic, or group) through a single consistent interface. Key concepts include:

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

## Future Development

The simulation system roadmap includes:

1. **API Integration**: Exposing simulation capabilities through REST API
2. **Frontend Integration**: Enhanced UI for configuring and viewing simulations
3. **Performance Optimization**: Caching and parallel processing improvements
4. **Extended Entity Templates**: More diverse entity archetypes for varied simulations 