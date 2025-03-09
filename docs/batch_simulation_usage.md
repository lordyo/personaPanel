# Batch Simulation Usage Guide

This guide provides step-by-step instructions on how to use the batch simulation feature with practical examples.

## Prerequisites

- A running instance of the application
- Entities created in the database

## Approach 1: Using the Test Script

The simplest way to run a batch simulation is with the provided test script.

```bash
# Basic usage with default parameters
./test_batch_simulation.sh

# Custom parameters
./test_batch_simulation.sh entity_ids.json "AI Ethics Discussion" 2 5 "AI Ethics Panel" "Exploring AI ethics viewpoints"
```

### Parameters:
1. Entity IDs file or comma-separated list (default: "entity_ids.json")
2. Context (default: "A group discussion about climate change solutions") 
3. Interaction size (default: 2)
4. Number of simulations (default: 3)
5. Batch name (default: "Test Batch Simulation")
6. Description (default: "A batch simulation for testing purposes")

## Approach 2: Using the Command-Line Script Directly

For more control, use the batch simulation script directly:

```bash
# Activate the virtual environment
source venv/bin/activate

# Run with specific parameters
python3 backend/scripts/run_batch_simulation.py \
    --entities "entity_ids.json" \
    --context "A panel discussion about AI ethics" \
    --interaction-size 2 \
    --num-simulations 3 \
    --name "AI Ethics Panel" \
    --description "Exploring diverse perspectives on AI ethics" \
    --n-turns 2 \
    --simulation-rounds 1
```

### Creating an entity_ids.json File

Before running the batch simulation, you need to create a file with entity IDs. Here's a Python script to help you:

```python
#!/usr/bin/env python3
"""
Script to create an entity_ids.json file with real entity IDs from the database.
"""

import os
import sys
import json

# Add the backend directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the storage module
import storage

def main():
    """Create an entity_ids.json file with real entity IDs."""
    print("Fetching entity types from database...")
    entity_types = storage.get_all_entity_types()
    
    if not entity_types:
        print("No entity types found in database.")
        return
    
    print(f"Found {len(entity_types)} entity type(s):")
    for i, entity_type in enumerate(entity_types):
        print(f"{i+1}. {entity_type['name']} (ID: {entity_type['id']})")
    
    choice = input("\nSelect entity type number to use (or 'all' for all types): ")
    
    entity_ids = []
    
    if choice.lower() == 'all':
        # Get entities from all types
        for entity_type in entity_types:
            entities = storage.get_entities_by_type(entity_type['id'])
            if entities:
                new_ids = [entity['id'] for entity in entities]
                print(f"Found {len(new_ids)} entities for type {entity_type['name']}")
                entity_ids.extend(new_ids)
    else:
        try:
            index = int(choice) - 1
            if 0 <= index < len(entity_types):
                entity_type = entity_types[index]
                entities = storage.get_entities_by_type(entity_type['id'])
                if entities:
                    entity_ids = [entity['id'] for entity in entities]
                    print(f"Found {len(entity_ids)} entities for type {entity_type['name']}")
                else:
                    print(f"No entities found for type {entity_type['name']}")
            else:
                print(f"Invalid selection. Please choose a number between 1 and {len(entity_types)}.")
                return
        except ValueError:
            print("Invalid input. Please enter a number or 'all'.")
            return
    
    if not entity_ids:
        print("No entity IDs found.")
        return
    
    # Limit the number of entities if needed
    max_entities = input(f"\nFound {len(entity_ids)} total entities. How many to include? (default: all): ")
    if max_entities.strip():
        try:
            max_entities = int(max_entities)
            entity_ids = entity_ids[:max_entities]
        except ValueError:
            print("Invalid input. Using all entities.")
    
    # Save to file
    filename = input("\nEnter filename to save entity IDs (default: entity_ids.json): ")
    if not filename.strip():
        filename = "entity_ids.json"
    
    with open(filename, 'w') as f:
        json.dump(entity_ids, f)
    
    print(f"Saved {len(entity_ids)} entity IDs to {filename}")
    return filename

if __name__ == "__main__":
    main()
```

Save this as `create_entity_ids.py`, make it executable (`chmod +x create_entity_ids.py`), and run it to create your entity_ids.json file.

## Approach 3: Using the REST API

For integration with frontend applications, use the REST API:

```bash
# Ensure your app is running
curl -X POST http://localhost:5000/api/batch-simulations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Historical Figures on Technology",
    "description": "Historical figures discussing modern technology",
    "context": "A roundtable discussion about the impact of artificial intelligence on society",
    "entity_ids": ["id1", "id2", "id3", "id4", "id5"],
    "interaction_size": 2,
    "num_simulations": 5,
    "n_turns": 3,
    "simulation_rounds": 1,
    "metadata": {
      "category": "technology",
      "tags": ["AI", "history", "perspectives"]
    }
  }'
```

## Real-World Examples

### Example 1: Marketing Research

Simulate reactions of diverse personas to a marketing message:

```bash
# Create entity_ids.json with customer personas
# Then run:
./test_batch_simulation.sh entity_ids.json "Your reaction to the slogan: 'The Future is Now with TechCorp'" 1 10 "Marketing Research" "Testing slogan reactions"
```

### Example 2: Political Debates

Simulate discussions between political figures on current issues:

```bash
# With political figure entities:
python3 backend/scripts/run_batch_simulation.py \
    --entities "political_figures.json" \
    --context "A debate about climate change policy" \
    --interaction-size 2 \
    --num-simulations 6 \
    --name "Climate Policy Debates" \
    --description "Simulated debates on climate policy" \
    --n-turns 3
```

### Example 3: Team Dynamics

Test how different team compositions might function:

```bash
# With team member personality types:
python3 backend/scripts/run_batch_simulation.py \
    --entities "personality_types.json" \
    --context "A team meeting to plan a new product launch" \
    --interaction-size 4 \
    --num-simulations 5 \
    --name "Team Dynamics Simulation" \
    --description "Testing different team compositions"
```

## Viewing Batch Simulation Results

### Via API

```bash
# Get all batches
curl http://localhost:5000/api/batch-simulations

# Get a specific batch (replace BATCH_ID with actual ID)
curl http://localhost:5000/api/batch-simulations/BATCH_ID

# Export results to JSON
curl -o results.json http://localhost:5000/api/batch-simulations/BATCH_ID/export?format=json

# Export results to CSV
curl -o results.csv http://localhost:5000/api/batch-simulations/BATCH_ID/export?format=csv
```

### Analyzing Results

Once you've exported the results, you can analyze them with tools like:
- Excel or Google Sheets (for CSV data)
- Python with pandas (for more advanced analysis)
- Visualization tools like Tableau or Power BI

## Troubleshooting

1. **"No such table: simulation_batches"**
   - Run `python3 initialize_db.py` to create the required tables

2. **"No valid entities found"**
   - Ensure the entity IDs in your file actually exist in the database
   - Try running with fewer entities if you're hitting limits

3. **"Cannot create combinations"**
   - Check that you have enough entities for the interaction size you specified
   - Reduce the interaction size or increase the number of entities

## Best Practices

1. **Start small**: Begin with a small number of simulations and entities to ensure everything works
2. **Use realistic contexts**: More specific and realistic contexts produce better quality simulations
3. **Balance interaction size**: Larger interaction sizes create more complex discussions but require more resources
4. **Save and compare results**: Export results in CSV format for easy comparison across multiple batches 