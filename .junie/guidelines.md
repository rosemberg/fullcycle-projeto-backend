# Project Development Guidelines

This document provides guidelines and information for developing and maintaining the Codeflix Catalog Admin project.

## Build/Configuration Instructions

### Environment Setup

1. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```bash
   python manage.py migrate
   # or use the Makefile command
   make migrate
   ```

### Running the Application

1. Start RabbitMQ (required for event processing):
   ```bash
   docker run -d --hostname rabbitmq --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
   ```

2. Start the message consumer:
   ```bash
   python manage.py startconsumer
   # or use the Makefile command
   make startconsumer
   ```

3. Run the development server:
   ```bash
   python manage.py runserver
   # or use the Makefile command
   make run
   ```

### Makefile Commands

The project includes a Makefile with useful commands:

- `make startconsumer`: Starts the RabbitMQ container (if not running) and runs the Django consumer
- `make stopconsumer`: Stops and removes the RabbitMQ container
- `make migrate`: Runs Django migrations
- `make run`: Starts the Django development server
- `make shell`: Opens the Django shell_plus

## Testing Information

### Test Structure

The project follows a structured approach to testing:

1. **Domain Tests**: Test domain models and entities
   - Located in `src/core/<module>/tests/domain/`

2. **Application Tests**:
   - **Unit Tests**: Test use cases in isolation with mocked dependencies
     - Located in `src/core/<module>/tests/application/use_cases/unit/`
   - **Integration Tests**: Test use cases with actual dependencies
     - Located in `src/core/<module>/tests/application/use_cases/integration/`

3. **Infrastructure Tests**: Test repository implementations and other infrastructure components
   - Located in `src/core/<module>/tests/infra/`

### Running Tests

Tests are run using pytest:

```bash
# Run all tests
python -m pytest

# Run tests for a specific module
python -m pytest src/core/category/

# Run a specific test file
python -m pytest src/core/category/tests/domain/test_category.py

# Run tests with verbose output
python -m pytest -v

# Run tests matching a specific pattern
python -m pytest -k "test_create_category"
```

### Creating New Tests

When creating new tests, follow these guidelines:

1. Place tests in the appropriate directory based on what they're testing (domain, application, infrastructure)
2. Organize tests into classes based on the functionality being tested
3. Use descriptive test method names that explain what's being tested
4. Follow the Arrange-Act-Assert pattern in test methods

#### Example Test

Here's an example of a simple test:

```python
import pytest
import uuid
from .utils import is_valid_uuid

class TestIsValidUUID:
    def test_valid_uuid_returns_true(self):
        # Generate a valid UUID
        valid_uuid = str(uuid.uuid4())
        
        # Test the function
        result = is_valid_uuid(valid_uuid)
        
        # Assert the result
        assert result is True
    
    def test_invalid_uuid_returns_false(self):
        # Test with an invalid UUID
        invalid_uuid = "not-a-uuid"
        
        # Test the function
        result = is_valid_uuid(invalid_uuid)
        
        # Assert the result
        assert result is False
```

## Development Guidelines

### Project Architecture

The project follows a clean architecture approach with the following layers:

1. **Domain Layer**: Contains the core business logic and entities
   - Located in `src/core/<module>/domain/`
   - Entities are implemented as Python dataclasses
   - Includes validation logic and business rules

2. **Application Layer**: Contains use cases that orchestrate the domain entities
   - Located in `src/core/<module>/application/`
   - Use cases are implemented as classes with an `execute` method
   - Uses request/response DTOs for input/output
   - Translates domain exceptions to application-specific exceptions

3. **Infrastructure Layer**: Contains implementations of repositories and other external interfaces
   - Located in `src/core/<module>/infra/`
   - Includes database repositories, API clients, etc.

4. **Presentation Layer**: Contains the API endpoints and controllers
   - Located in `src/django_project/`
   - Implemented using Django and Django REST Framework

### Code Style

1. **Domain Entities**:
   - Use Python dataclasses
   - Include validation in the `__post_init__` method
   - Override `__str__` and `__repr__` methods for better debugging

2. **Use Cases**:
   - Implement as classes with an `execute` method
   - Use dependency injection through the constructor
   - Define request/response DTOs as dataclasses

3. **Testing**:
   - Organize tests into classes based on functionality
   - Use descriptive test method names
   - Follow the Arrange-Act-Assert pattern

### Event-Driven Architecture

The project uses RabbitMQ for event processing:

1. Domain events are published when entities are created, updated, or deleted
2. Consumers process these events asynchronously
3. The `startconsumer` command starts the event consumer

### Error Handling

The project uses a notification pattern for validation errors:

1. Errors are collected in a notification object
2. Multiple errors can be accumulated before raising an exception
3. Exceptions include all collected error messages