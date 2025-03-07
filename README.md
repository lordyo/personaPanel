# Entity Simulation Framework

A extensible, LLM-powered framework that enables users to simulate interactions between diverse virtual entities, providing insights through synthetic qualitative research, creative ideation, and scenario exploration.

## Project Overview

This framework provides a foundation for creating and simulating diverse virtual entities. By leveraging LLMs through DSPy, the system can generate creative and insightful interactions without requiring complex rule-based programming.

## Features (Planned)

- Entity type definition with customizable dimensions
- LLM-powered entity instance generation
- Context-based entity simulations
- Solo, dyadic, and group interaction types
- Results visualization and analysis

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+ and npm
- OpenAI API key or compatible LLM provider

### Python Environment Setup

If you're experiencing issues with Python in Cursor IDE or other environments, we've provided scripts to help set up a clean Python environment:

1. **Diagnose Python Issues**
   ```bash
   ./diagnose_python.py
   ```
   This script checks your Python installation and configuration, identifying common issues and providing recommendations.

2. **Set Up Python Environment**
   ```bash
   ./setup_python_env.sh
   ```
   This script creates a virtual environment, installs dependencies, and sets up helper scripts for running the application and tests.

3. **Helper Scripts**
   - `./activate-env` - Activates the virtual environment
   - `./run-app` - Runs the backend application in the virtual environment
   - `./run-tests` - Runs tests in the virtual environment

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd entity-simulation-framework
```

2. Install Python dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Install frontend dependencies
```bash
cd frontend
npm install
```

4. Set up environment variables
```bash
cp .env.example .env
```
Edit the `.env` file to include your LLM API keys and other configuration.

5. Initialize the database
```bash
python backend/scripts/initialize_db.py
```

### Running the Application

1. Start the backend server
```bash
python backend/scripts/run_server.py
```

2. In another terminal, start the frontend development server
```bash
cd frontend
npm start
```

3. Access the application at `http://localhost:3000`

## Project Structure

```
entity-simulation-framework/
├── backend/                  # Python backend
│   ├── app.py                # Main Flask application
│   ├── storage.py            # Database operations
│   ├── core/                 # Core entity and simulation models
│   │   ├── dimension.py      # Dimension types definition
│   │   ├── entity.py         # Entity type and instance models
│   │   ├── simulation.py     # Simulation engine
│   │   └── templates.py      # Predefined entity templates
│   ├── llm/                  # LLM integration
│   │   ├── dspy_modules.py   # DSPy module implementation
│   │   └── prompts.py        # Prompt templates
│   └── scripts/              # Utility scripts
│       ├── initialize_db.py  # Database initialization
│       └── run_server.py     # Server startup script
├── frontend/                 # React frontend
│   ├── public/               # Static assets
│   └── src/                  # React source code
│       ├── components/       # Reusable UI components
│       ├── pages/            # Main application pages
│       ├── services/         # API client services
│       └── utils/            # Utility functions
├── data/                     # Data storage
│   ├── cache/                # LLM response cache
│   └── entity_sim.db         # SQLite database (created on init)
├── docs/                     # Documentation
├── tests/                    # Tests
│   ├── backend/              # Backend tests
│   └── frontend/             # Frontend tests
├── diagnose_python.py        # Python diagnostic script
├── setup_python_env.sh       # Python environment setup script
├── activate-env              # Virtual environment activation script
├── run-app                   # Application runner script
└── run-tests                 # Test runner script
```

## Backend Infrastructure

The backend infrastructure (Epic 4) includes the following components:

### Database Schema

- **SQLite Database**: Lightweight, file-based database stored in `data/entity_sim.db`
- **Entity Types Table**: Stores entity type definitions with their dimensions
- **Entities Table**: Stores entity instances with their attributes
- **Contexts Table**: Stores simulation contexts
- **Simulations Table**: Stores simulation results with references to entities and contexts
- **Indices**: Performance optimized with appropriate indices

### DSPy Module Implementation

- **EntityGenerator**: Generates entity instances with attributes based on entity type dimensions
- **SoloInteractionSimulator**: Simulates how a single entity responds to a context
- **DyadicInteractionSimulator**: Simulates interactions between two entities in a context
- **GroupInteractionSimulator**: Simulates group dynamics among multiple entities
- **Caching Mechanism**: Response caching to reduce API usage
- **Error Handling**: Robust error handling with retries for API failures

### Flask API Server

- **RESTful Endpoints**: Clean API design following REST principles
- **CORS Support**: Configured for local development
- **Error Handling**: Comprehensive error handling with informative responses
- **Documentation**: Detailed docstrings for all API endpoints
- **Response Formatting**: Consistent response format for success and error cases

## Documentation

- [Backend Structure](backend/README.md) - Overview of the backend directory structure
- [Simulation Improvements](docs/simulation_improvements.md) - Documentation of the recent simulation system improvements

## License

[MIT License](LICENSE) 