# Backend Directory Structure

This directory contains the backend code for the PersonaPanel application.

## Directory Organization

- **core/**: Core entity and simulation models
  - Entity definitions
  - Dimension definitions
  - Base simulation functionality

- **database/**: Database initialization and management scripts
  - `init_db.py`: Basic database initialization
  - `initialize_db.py`: Comprehensive database setup with templates

- **llm/**: LLM integration modules
  - `interaction_module.py`: Unified entity interaction simulator
  - `dspy_modules.py`: DSPy modules for entity generation and other tasks
  - `prompts.py`: Prompt templates for LLM interactions

- **logs/**: Log files directory
  - Contains application logs and simulation result logs

- **scripts/**: Legacy script directory
  - Contains original scripts (retained for compatibility)
  - New scripts have been moved to their respective directories

- **simulations/**: Simulation-related scripts and configurations
  - `run_simulation.py`: Main simulation runner script
  - `run_simulation_tests.py`: Tests for the simulation functionality
  - `run_simulation_tests.sh`: Shell script for running simulation tests
  - **config/**: Simulation configuration files
    - Sample entity and simulation configuration files

- **utilities/**: Utility scripts
  - `create_env.py`: Script for creating .env file with default values

## Main Files

- **app.py**: Main Flask application and API endpoints
- **storage.py**: Database interface and operations

## Running the Backend

1. Make sure you have a virtual environment activated:
   ```
   source venv/bin/activate
   ```

2. Initialize the database (if not already done):
   ```
   python backend/database/initialize_db.py
   ```

3. Start the backend server:
   ```
   python backend/scripts/run_server.py
   ```

## Running Simulations

To run a simulation:
```
python backend/simulations/run_simulation.py --config path/to/config.json --entities path/to/entities.json
```

To run simulation tests:
```
cd backend/simulations
./run_simulation_tests.sh
``` 