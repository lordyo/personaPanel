# Persona Panel

A comprehensive framework for creating, managing, and utilizing AI personas for various applications. This project enables the generation of diverse, coherent personas based on customizable dimensions, and facilitates interactions between these personas.

## Project Structure

The project consists of two main components:

- **Frontend**: A React-based web application for interacting with the persona framework
- **Backend**: A Python-based API server that handles persona generation, validation, and persistence using DSPy and Claude

## Features

- **Dimension Management**: Define and customize the traits that make up personas
- **Persona Generation**: Create diverse personas based on specified dimensions using Claude and DSPy
- **Persona Library**: Save, view, and edit personas
- **Multi-Persona Discussions**: Generate discussions between different personas on various topics
- **Validation**: Ensure personas are coherent and realistic
- **Settings**: Configure application behavior

## Getting Started

### Prerequisites

- Node.js (v14+) for the frontend
- Python (v3.8+) for the backend
- npm or yarn for frontend package management
- Anthropic API key for Claude access

### Quick Start

1. Clone this repository
2. Set up environment variables:
   ```
   # Create a .env file in the root directory
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```
3. Install backend dependencies:
   ```
   pip install -r requirements.txt
   pip install -e .  # Install the persona_framework package
   ```
4. Start the backend server:
   ```
   python backend_server.py
   ```
5. Start the frontend:
   ```
   cd frontend/persona-panel
   npm install
   npm start
   ```
6. Start the JSON Server for data persistence:
   ```
   cd frontend/persona-panel
   npx json-server --watch db.json --port 5000
   ```

## Frontend

The frontend is a React application built with TypeScript and Material UI. It provides a user-friendly interface for interacting with the persona framework.

See the [frontend README](frontend/persona-panel/README.md) for more details.

## Backend

The backend is implemented using Python, FastAPI, and DSPy. It provides the API for persona generation, validation, and persistence. It leverages DSPy and Claude for the underlying persona generation capabilities.

### Backend API Endpoints

- `GET /`: Check if the server is running
- `POST /api/personas/generate`: Generate personas using DSPy and Claude

## Development Status

- ✅ Frontend UI implementation
- ✅ Mock data for development
- ✅ Backend API implementation
- ✅ Integration with DSPy
- ⏳ Deployment documentation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [DSPy](https://github.com/stanfordnlp/dspy) - The underlying framework for persona generation
- [Material UI](https://mui.com/) - React component library
- [Solarized](https://ethanschoonover.com/solarized/) - Color scheme 