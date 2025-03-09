# Batch Simulations

The batch simulation feature enables running multiple simulations in parallel with configurable parameters. This is particularly useful for synthetic empirical research, where you want to test how multiple different entity combinations react to the same context or prompt.

## Overview

Batch simulations allow you to:

1. **Run multiple simulations at once** - Run many simulations in parallel instead of one at a time
2. **Group results logically** - Organize related simulations into batches for easier analysis
3. **Combine different entities** - Automatically create combinations of entities for simulations
4. **Export batch results** - Export all simulation results from a batch in JSON or CSV format

## How Batch Simulations Work

A batch simulation consists of:

1. A shared context that applies to all simulations in the batch
2. A set of entities to be used in the simulations
3. Configuration for how to combine entities (interaction size)
4. The number of simulations to run in the batch
5. Simulation parameters (turns per round, number of rounds)

The system automatically generates combinations of entities based on the specified interaction size and runs the requested number of simulations in parallel.

## Entity Combinations

The number of possible combinations is calculated based on:

- Number of entities selected (`n`)
- Interaction size (`k`)

Formula: `C(n,k) = n! / (k! * (n-k)!)`

For example:
- 10 entities with interaction size 1 = 10 possible simulations (solo)
- 10 entities with interaction size 2 = 45 possible simulations (dyadic)
- 10 entities with interaction size 3 = 120 possible simulations (group)

## API Endpoints

### Create a Batch Simulation

```
POST /api/batch-simulations
```

**Request Body:**
```json
{
  "name": "Climate Change Discussion",
  "description": "Simulating how different entities discuss climate change solutions",
  "context": "A panel discussion about potential solutions to climate change",
  "entity_ids": ["entity-id-1", "entity-id-2", "entity-id-3", "entity-id-4"],
  "interaction_size": 2,
  "num_simulations": 3,
  "n_turns": 2,
  "simulation_rounds": 1,
  "metadata": {
    "category": "climate",
    "tags": ["environment", "discussion"]
  }
}
```

**Parameters:**
- `name`: Name for the batch (required)
- `description`: Description of the batch (optional)
- `context`: Context for all simulations in the batch (required)
- `entity_ids`: Array of entity IDs to use in simulations (required)
- `interaction_size`: Number of entities per simulation (required)
- `num_simulations`: Number of simulations to run (required)
- `n_turns`: Number of dialogue turns per simulation round (optional, default: 1)
- `simulation_rounds`: Number of simulation rounds (optional, default: 1)
- `metadata`: Additional metadata for the batch (optional)

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "batch-12345",
    "message": "Batch simulation started"
  }
}
```

### Get All Batch Simulations

```
GET /api/batch-simulations
```

**Query Parameters:**
- `include_simulations`: Whether to include all simulations in each batch (default: false)

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "batch-12345",
      "name": "Climate Change Discussion",
      "timestamp": "2025-03-07T12:34:56Z",
      "description": "Simulating how different entities discuss climate change solutions",
      "context": "A panel discussion about potential solutions to climate change",
      "status": "completed",
      "metadata": {
        "category": "climate",
        "tags": ["environment", "discussion"]
      }
    },
    // More batches...
  ]
}
```

### Get a Specific Batch Simulation

```
GET /api/batch-simulations/:batch_id
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "batch-12345",
    "name": "Climate Change Discussion",
    "timestamp": "2025-03-07T12:34:56Z",
    "description": "Simulating how different entities discuss climate change solutions",
    "context": "A panel discussion about potential solutions to climate change",
    "status": "completed",
    "metadata": {
      "category": "climate",
      "tags": ["environment", "discussion"]
    },
    "simulations": [
      {
        "id": "sim-12345",
        "sequence_number": 1,
        "timestamp": "2025-03-07T12:35:23Z",
        "interaction_type": "dyadic",
        "entity_ids": ["entity-id-1", "entity-id-2"],
        "content": "Entity 1: *thinking*\n\"Dialog content...\"\n\nEntity 2: *thinking*\n\"Dialog response...\"",
        "metadata": {
          "n_turns": 2,
          "simulation_rounds": 1,
          "final_turn_number": 2
        }
      },
      // More simulations...
    ]
  }
}
```

### Delete a Batch Simulation

```
DELETE /api/batch-simulations/:batch_id
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "message": "Batch simulation batch-12345 deleted successfully"
  }
}
```

### Export Batch Simulation Data

```
GET /api/batch-simulations/:batch_id/export?format=json
```

**Query Parameters:**
- `format`: Export format (json or csv, default: json)

**Response:** A file download with the batch simulation data in the specified format.

## Command-Line Usage

You can also run batch simulations using the provided command-line script:

```bash
python3 backend/scripts/run_batch_simulation.py \
    --entities "entity_ids.json" \
    --context "A panel discussion about climate change solutions" \
    --interaction-size 2 \
    --num-simulations 3 \
    --name "Climate Change Discussions" \
    --description "Testing how different entities discuss climate solutions" \
    --n-turns 2 \
    --simulation-rounds 1
```

### Parameters:
- `--entities`: Comma-separated list of entity IDs or path to JSON file with entity IDs
- `--interaction-size`: Number of entities per interaction (1=solo, 2=dyadic, 3+=group)
- `--num-simulations`: Number of simulations to run in the batch
- `--context`: Context description or path to file with context
- `--name`: Name for the batch (optional)
- `--description`: Description for the batch (optional)
- `--n-turns`: Number of turns per simulation round (optional, default: 1)
- `--simulation-rounds`: Number of simulation rounds (optional, default: 1)

## Batch Status Values

Batches can have the following status values:

- `pending`: Batch has been created but simulations haven't started yet
- `in_progress`: Batch simulations are currently running
- `completed`: All simulations in the batch completed successfully
- `partial`: Some simulations completed, but others failed
- `failed`: All simulations in the batch failed

## Example Usage Scenario

1. **Select entities**: Choose a set of entities (e.g., 10 historical figures)
2. **Define the context**: Create a prompt (e.g., "Discuss the ethics of artificial intelligence")
3. **Configure interaction**: Choose the interaction size (e.g., 2 for pairs)
4. **Set batch size**: Decide how many simulations to run (e.g., 20 pairs)
5. **Run the batch**: Start the batch simulation
6. **Analyze results**: Review each simulation in the batch or export for external analysis

This approach allows you to collect a diverse set of perspectives and reactions to the same prompt, enabling synthetic empirical research on how different entity combinations respond. 