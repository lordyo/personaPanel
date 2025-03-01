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

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd entity-simulation-framework
```

2. Install Python dependencies
```bash
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
python backend/scripts/init_db.py
```

### Running the Application

1. Start the backend server
```bash
python backend/app.py
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
│   ├── config/               # Configuration files
│   ├── controllers/          # API route handlers
│   ├── models/               # Data models
│   ├── scripts/              # Utility scripts
│   └── services/             # Business logic
│       ├── entity/           # Entity management services
│       ├── llm/              # LLM integration services
│       └── simulation/       # Simulation engine services
├── frontend/                 # React frontend
│   ├── public/               # Static assets
│   └── src/                  # React source code
│       ├── components/       # Reusable UI components
│       ├── pages/            # Main application pages
│       ├── services/         # API client services
│       └── utils/            # Utility functions
├── data/                     # Data storage
│   └── db.sqlite             # SQLite database (created on init)
├── docs/                     # Documentation
└── tests/                    # Tests
    ├── backend/              # Backend tests
    └── frontend/             # Frontend tests
```

## Documentation

See the `docs/` directory for detailed technical specifications and development guidelines.

## License

[MIT License](LICENSE) 