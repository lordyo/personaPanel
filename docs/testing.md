# Testing the Entity Simulation Framework

This document outlines the testing strategy for the Entity Simulation Framework, focusing on the Entity Type Management functionality.

## Test Environment Setup

### Backend Testing Requirements
- Python 3.x
- pytest
- pytest-cov (for coverage reports)

### Frontend Testing Requirements
- Node.js
- Jest
- React Testing Library

## Running Tests

We provide a script that runs all tests for both backend and frontend:

```bash
# From the project root directory
./tests/run_tests.sh
```

This script will:
1. Set up a virtual environment if one doesn't exist
2. Install necessary test dependencies
3. Run backend API tests
4. Run frontend component tests (if the frontend environment is set up)

## Test Categories

### 1. Backend API Tests

Located in `tests/test_*.py` files, these tests check the functionality of all API endpoints:

- **Template API Tests** (`test_api_templates.py`): Tests for template listing, retrieval, and entity type creation from templates.
- **Entity Type API Tests** (`test_entity_types.py`): Tests for entity type creation, validation, and retrieval.

### 2. Frontend Component Tests

Located in `frontend/src/components/__tests__/*.test.js` files:

- **Component Tests**: Verify that UI components render correctly and respond to user interactions.
- **Page Tests**: Ensure that page components integrate correctly with services and display data appropriately.

### 3. Manual Testing Checklist

For certain aspects of the application, manual testing is also important:

#### Entity Type Creation
- [ ] Can view the list of predefined templates
- [ ] Can create a new entity type from a template
- [ ] Can customize template dimensions before creating an entity type
- [ ] Can create a new entity type from scratch
- [ ] Form validation works correctly for required fields
- [ ] Form validation works correctly for different dimension types

#### Entity Type Management
- [ ] Can view a list of created entity types
- [ ] Entity types display correct information
- [ ] Can navigate between entity type list and creation views
- [ ] Error states are handled gracefully

## Test Coverage

To generate a test coverage report for the backend:

```bash
python -m pytest --cov=backend tests/
```

To generate a test coverage report for the frontend:

```bash
cd frontend && npm test -- --coverage
```

## Troubleshooting Tests

### Backend Test Issues
- Ensure you're running tests from the project root directory
- Check that the virtual environment is activated and dependencies are installed
- Verify that the database schema matches what the tests expect

### Frontend Test Issues
- Ensure all node dependencies are installed
- Check for errors in the component props or rendering logic
- Verify that mock functions are properly configured 