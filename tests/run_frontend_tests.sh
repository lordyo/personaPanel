#!/bin/bash
# Run frontend tests for the Entity Simulation Framework
# This script focuses only on frontend tests, avoiding Python environment issues

# Change to the project root directory
cd "$(dirname "$0")/.." || { echo "Failed to change to project root directory"; exit 1; }
PROJECT_ROOT=$(pwd)

echo "Running frontend tests from: $PROJECT_ROOT"

# Check if frontend directory exists
if [ ! -d "$PROJECT_ROOT/frontend" ]; then
    echo "Error: frontend directory not found"
    exit 1
fi

# Navigate to frontend directory
cd "$PROJECT_ROOT/frontend" || { echo "Failed to change to frontend directory"; exit 1; }

# Check if node_modules exists, if not suggest installation
if [ ! -d "node_modules" ]; then
    echo "node_modules directory not found. Installing dependencies..."
    npm install || { echo "Failed to install dependencies. Please run 'npm install' manually."; exit 1; }
fi

# Run frontend tests in non-watch mode
echo "Running frontend component tests..."
npm test -- --watchAll=false

echo "Frontend tests completed!" 