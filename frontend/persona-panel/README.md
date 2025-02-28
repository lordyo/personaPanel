# Persona Panel Frontend

A React-based frontend for the GenAI Persona Framework, allowing users to create, manage, and utilize AI personas for various applications.

## Features

- **Dimension Management**: Create and manage dimensions that define persona traits
- **Persona Generation**: Generate diverse personas based on customizable dimensions
- **Persona Library**: Save, view, and edit personas
- **Multi-Persona Discussions**: Create discussions between different personas on various topics
- **Validation**: Ensure personas are coherent and realistic
- **Settings**: Configure application behavior

## Tech Stack

- **React**: Frontend library
- **TypeScript**: Type-safe JavaScript
- **Material UI**: Component library with Solarized Dark theme
- **React Router**: Navigation and routing
- **Axios**: API communication

## Getting Started

### Prerequisites

- Node.js (v14+)
- npm or yarn

### Installation

1. Clone the repository
2. Navigate to the frontend directory:
   ```
   cd frontend/persona-panel
   ```
3. Install dependencies:
   ```
   npm install
   ```
   or
   ```
   yarn install
   ```

### Running the Development Server

```
npm start
```
or
```
yarn start
```

The application will be available at [http://localhost:3000](http://localhost:3000).

### Building for Production

```
npm run build
```
or
```
yarn build
```

## Project Structure

```
src/
├── components/         # Reusable UI components
│   ├── common/         # Shared components (Layout, etc.)
│   ├── dimensions/     # Dimension-related components
│   ├── personas/       # Persona-related components
│   └── discussions/    # Discussion-related components
├── pages/              # Page components
├── services/           # API services
│   └── mockData/       # Mock data for development
├── theme/              # Theme configuration
├── types/              # TypeScript interfaces
└── utils/              # Utility functions
```

## Connecting to the Backend

By default, the frontend uses mock data for development. To connect to a real backend:

1. Set the `REACT_APP_API_URL` environment variable to your backend URL
2. Ensure the backend implements the expected API endpoints

## Customization

### Theme

The application uses a custom Solarized Dark theme. You can modify the theme in `src/theme/solarizedDarkTheme.ts`.

### Mock Data

During development, the application uses mock data from `src/services/mockData/`. You can modify these files to test different scenarios.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [DSPy](https://github.com/stanfordnlp/dspy) - The underlying framework for persona generation
- [Solarized](https://ethanschoonover.com/solarized/) - Color scheme
