# FastAPI MVC Application

This project follows an MVC architecture with a service layer using FastAPI, incorporating database migrations with Alembic, Docker containerization, workers and schedulers.

## Project Structure

```
baseFastApiMVC/
├── app/
│   ├── config/         # Configuration files and settings
│   ├── controllers/    # Route handlers (controllers)
│   ├── models/         # Database models and entities
│   ├── services/       # Business logic layer
│   ├── repositories/   # Data access layer
│   ├── schemas/        # Pydantic models for request/response
│   ├── middlewares/    # Custom middleware functions
│   ├── utils/          # Utility functions and helpers
│   ├── workers/        # Background worker implementations
│   ├── jobs/           # Scheduled job definitions
│   └── __init__.py
├── tests/              # Test suite
├── alembic/            # Database migration files
├── scripts/            # Utility scripts for project management
├── main.py             # Application entry point
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
├── .env                # Environment variables (not in repo)
├── .env.example        # Example environment variables
├── .gitignore          # Git ignore file
├── README.md           # Project documentation
└── pyproject.toml      # Poetry dependencies and project metadata
```

## Features

- MVC architecture with service layer
- FastAPI web framework
- Poetry for dependency management
- OOP-based design
- Comprehensive logging system
- Background workers with Celery
- Scheduled tasks with APScheduler
- SQL database integration with SQLAlchemy
- Database migrations with Alembic
- Docker containerization with PostgreSQL support
- Redis integration for caching and task queues

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Poetry package manager
- PostgreSQL database
- Redis (for Celery workers)
- Docker and Docker Compose (optional, for containerized deployment)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd baseFastApiMVC
   ```

2. Install dependencies:
   ```
   poetry install
   ```

3. Set up environment variables:
   ```
   cp .env.example .env
   # Edit the .env file with your configuration
   ```

4. Set up the database:
   ```
   # Create a PostgreSQL database
   createdb fastapi_mvc  # If using PostgreSQL CLI
   
   # Apply database migrations
   poetry run python scripts/manage_migrations.py upgrade
   ```

### Running the Application

1. Start the API server:
   ```
   poetry run uvicorn main:app --reload
   ```

2. Start Celery worker:
   ```
   poetry run celery -A app.workers.celery_worker worker --loglevel=info
   ```

3. Start the scheduler:
   ```
   poetry run python -m app.jobs.scheduler
   ```

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Database Migrations

The project uses Alembic for database migration management. A helper script is provided in `scripts/manage_migrations.py` to make migration operations easier.

```bash
# Create a new migration with auto-detection of model changes
poetry run python scripts/manage_migrations.py create -m "description"description"

# Apply migrations
poetry run python scripts/manage_migrations.py upgrade

# Rollback migrations
poetry run python scripts/manage_migrations.py downgrade

# Get migration history
poetry run python scripts/manage_migrations.py history

# Rollback to a specific revision
poetry run python scripts/manage_migrations.py downgrade -r <revision_id>
```

#### Migration Strategy

Migrations are managed using Alembic with autogenerate capability. When you make changes to your SQLAlchemy models:

1. Create a new migration:
   ```bash
   poetry run python scripts/manage_migrations.py create -m "Description of your model changes"
   ```

2. Verify the generated migration script in `alembic/versions/`

3. Apply the migration:
   ```bash
   poetry run python scripts/manage_migrations.py upgrade
   ```

### Docker Setup

The project includes Docker configuration for easy deployment and development.

#### Prerequisites
- Docker and Docker Compose installed on your system

#### Running with Docker

1. Build and start all services:
   ```bash
   docker-compose up --build
   ```

   This will start:
   - FastAPI application on port 8000
   - PostgreSQL database on port 5432
   - Redis on port 6379
   - Celery worker

2. To run in detached mode:
   ```bash
   docker-compose up -d
   ```

3. To stop all services:
   ```bash
   docker-compose down
   ```

#### Database Management with Docker

The Docker setup automatically:
- Waits for the PostgreSQL database to be ready
- Applies any pending migrations
- Creates initial data if needed

#### Accessing Services

- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Database: PostgreSQL on localhost:5432
  - User: postgres
  - Password: postgres
  - Database: fastapi_mvc

### Running Tests

The project has a comprehensive test suite focused on API testing. Tests follow the AAA (Arrange-Act-Assert) pattern for clarity and maintainability.

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=app

# Run specific test file
poetry run pytest tests/api/test_health.py

# Run tests with the helper script
poetry run python scripts/run_tests.py
```

#### Testing Best Practices

Our tests follow these best practices:

- **AAA Pattern**: All tests use the Arrange-Act-Assert pattern
- **Test Independence**: Each test is independent and doesn't rely on other tests
- **Clear Test Names**: Test names clearly describe what they're testing
- **Test Edge Cases**: We test both happy paths and error scenarios

For more information, see:
- [Testing Best Practices](docs/testing_best_practices.md)
- [Testing Framework Documentation](tests/README.md)

## Environment Variables

The application uses the following environment variables, which can be set in a `.env` file:

| Variable                      | Description                               | Default Value                                      |
|-------------------------------|-------------------------------------------|---------------------------------------------------|
| SERVER_HOST                   | Host to bind the server to                | 0.0.0.0                                            |
| SERVER_PORT                   | Port to bind the server to                | 8000                                               |
| DEBUG                         | Enable debug mode                         | True                                               |
| PROJECT_NAME                  | Name of the project                       | "FastAPI MVC Application"                          |
| PROJECT_DESCRIPTION           | Description of the project                | "FastAPI application following MVC architecture..." |
| PROJECT_VERSION               | Version of the project                    | "0.1.0"                                            |
| DATABASE_URL                  | Database connection URL                   | postgresql://postgres:postgres@localhost:5432/fastapi_mvc |
| DB_ECHO                       | Echo SQL statements                       | False                                              |
| AUTO_CREATE_TABLES            | Auto create tables on startup             | False                                              |
| LOG_LEVEL                     | Logging level                             | INFO                                               |
| LOG_FORMAT                    | Logging format                            | "{time:YYYY-MM-DD HH:mm:ss} \| {level} \| {message}" |
| LOG_FILE_PATH                 | Path to log file                          | logs/app.log                                       |
| REDIS_HOST                    | Redis host                                | localhost                                          |
| REDIS_PORT                    | Redis port                                | 6379                                               |
| REDIS_DB                      | Redis database                            | 0                                                  |
| CELERY_BROKER_URL             | Celery broker URL                         | redis://localhost:6379/0                           |
| CELERY_RESULT_BACKEND         | Celery result backend                     | redis://localhost:6379/0                           |
| JWT_SECRET_KEY                | Secret key for JWT                        | change_this_to_a_secure_secret                     |
| JWT_ALGORITHM                 | Algorithm for JWT                         | HS256                                              |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | JWT token expiration time in minutes    | 30                                                 |

## Project Scripts

The project includes several utility scripts in the `scripts/` directory:

### 1. `manage_migrations.py`

Helper script for managing Alembic migrations:

```bash
# Usage
poetry run python scripts/manage_migrations.py [command] [options]

# Commands:
# - create: Create a new migration
# - upgrade: Apply migrations
# - downgrade: Rollback migrations
# - history: View migration history
```

### 2. `docker-entrypoint.py`

Script that runs when the Docker container starts:

- Waits for the database to be available
- Applies any pending migrations
- Creates initial data if needed

### 3. `init_db.py`

Initializes the database with tables and seed data:

```bash
poetry run python scripts/init_db.py
```

## API Structure

The API follows RESTful design principles with versioning:

```
/api/v1/
├── health/          # Health check endpoints
├── users/           # User management
├── auth/            # Authentication endpoints
└── ...              # Other resource endpoints
```

The API is documented using OpenAPI/Swagger and can be accessed at:
- `/docs` - Swagger UI
- `/redoc` - ReDoc UI

## Architecture

### MVC with Service Layer

This project follows the Model-View-Controller (MVC) architecture with an additional service layer:

- **Models**: SQLAlchemy ORM models representing database tables
- **Views**: FastAPI response schemas (Pydantic models)
- **Controllers**: FastAPI route handlers
- **Services**: Business logic layer
- **Repositories**: Data access layer

### Application Layers

1. **Controller Layer** (`app/controllers/`):
   - Handles HTTP requests and responses
   - Validates input using Pydantic models
   - Delegates business logic to services

2. **Service Layer** (`app/services/`):
   - Contains business logic
   - Orchestrates operations using repositories
   - Handles data transformations

3. **Repository Layer** (`app/repositories/`):
   - Handles data access operations
   - Interacts with the database via SQLAlchemy
   - Provides CRUD operations

4. **Model Layer** (`app/models/`):
   - Define SQLAlchemy ORM models
   - Represents database structure

### Configuration

The application uses a settings-based configuration pattern:

- Environment variables are loaded through Pydantic Settings
- Default values are provided in `app/config/settings.py`
- Override defaults in `.env` file

#### Key Configuration Options

- **Database**: Connection details, echo mode, auto-create tables
- **Server**: Host, port, debug mode
- **Logging**: Level, format, file path
- **Redis & Celery**: Connection details, broker URL
- **JWT**: Secret key, algorithm, token expiration

## Deployment

### Docker Deployment

For production deployment using Docker:

1. Configure production settings in a `.env.prod` file
2. Build and run the Docker containers:
   ```bash
   docker-compose -f docker-compose.yml up --build -d
   ```

### Production Considerations

1. **Environment Variables**:
   - Set `DEBUG=False` for production
   - Use strong `JWT_SECRET_KEY` value
   - Configure proper `LOG_LEVEL` and `LOG_FILE_PATH`

2. **Database**:
   - Use connection pooling for better performance
   - Set up regular database backups
   - Consider database replication for high availability

3. **Security**:
   - Implement proper rate limiting
   - Set up HTTPS with SSL/TLS certificates
   - Configure proper CORS settings

4. **Monitoring**:
   - Set up application monitoring
   - Configure log aggregation
   - Implement health checks

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Developer Guides

The following guides are available to help new developers write code for this project correctly:

- [Models Guide](docs/models_guide.md) - How to create and work with database models
- [Repositories Guide](docs/repositories_guide.md) - How to implement the repository pattern
- [Services Guide](docs/services_guide.md) - How to implement the service layer
- [Controllers Guide](docs/controllers_guide.md) - How to create API endpoints and controllers
- [Testing Best Practices](docs/testing_best_practices.md) - How to write effective tests using AAA pattern
- [API Testing Guide](docs/api_testing_guide.md) - Detailed guide for testing REST APIs

These guides provide detailed instructions, examples, and best practices for maintaining clean, consistent code throughout the project.
