# Triad Model Setup Guide

This guide will help you set up the Triad Model - Westminster Parliamentary AI System.

## Prerequisites

- Python 3.11 or higher
- pip package manager
- Git (for version control)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/triad-model.git
cd triad-model
```

### 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to avoid dependency conflicts:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

With the virtual environment activated:

```bash
# Install the package in development mode
pip install -e .

# Or install from requirements.txt
pip install -r requirements.txt

# For development (includes testing tools)
pip install -e ".[dev]"
```

### 4. Set Up Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your specific configuration:
- `DATABASE_URL`: Database connection (SQLite by default: `file:./data/triad.db`)
- `ANTHROPIC_API_KEY`: Your Anthropic API key (required for Pydantic AI)
- `LOGFIRE_TOKEN`: Your Logfire token (optional but recommended)

### 5. Set Up Database

Initialize the Prisma database:

```bash
# Setup database schema and generate client
make db-setup

# Or manually
prisma generate
prisma db push
```

### 6. Verify Installation

Run the syntax check:

```bash
python scripts/check_syntax.py
```

Run the import check (requires dependencies installed):

```bash
python scripts/check_imports.py
```

### 6. Run Configuration Check

```bash
python scripts/start.py --check-config
```

### 7. Check Constitutional Compliance

```bash
python scripts/start.py --constitutional-check
```

## Running the Application

### Development Mode

```bash
# Using the startup script
python scripts/start.py --environment development

# Or using make
make run
```

### Production Mode

```bash
# Set environment
export TRIAD_ENV=production

# Run with production config
python scripts/start.py --environment production

# Or using make
make run-prod
```

## API Documentation

Once the server is running, you can access:

- API Documentation: http://localhost:8000/docs
- ReDoc Documentation: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

## Testing

Run the test suite:

```bash
# All tests
make test

# Specific test categories
make test-constitutional
make test-parliamentary
make test-integration
```

## Common Issues

### Import Errors

If you see import errors like "No module named 'logfire'":

1. Make sure you're in a virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Verify with: `python scripts/check_imports.py`

### macOS "externally-managed-environment" Error

This occurs on newer macOS versions. Always use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Permission Errors

If you get permission errors:

```bash
# Make scripts executable
chmod +x scripts/*.py
```

## Development Workflow

1. **Create a virtual environment** (always!)
2. **Install dependencies** in development mode
3. **Set up your .env file** with required credentials
4. **Run configuration checks** before starting
5. **Start the development server** with auto-reload
6. **Run tests** before committing changes

## Constitutional Framework

The system operates under Westminster parliamentary principles:

- **Separation of Powers**: Maintained between four agents
- **Parliamentary Accountability**: All decisions are logged
- **Constitutional Oversight**: Automatic compliance checking
- **Democratic Principles**: Transparent decision-making

## Getting Help

- Check the `/docs` directory for detailed documentation
- View API docs at http://localhost:8000/docs when running
- Run `make help` for available commands
- Check constitutional status at http://localhost:8000/api/v1/parliamentary/constitutional-status

## Next Steps

1. Explore the API documentation
2. Try the parliamentary procedures (Question Period, Motions)
3. Test agent interactions
4. Monitor system health and constitutional compliance
5. Review the architectural documentation in `/docs`