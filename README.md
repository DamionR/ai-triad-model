# Triad Model - AI Governance System 🏛️

An intelligent governance framework implementing proven Westminster-style separation of powers, adaptable for any organization - from Fortune 500 companies to personal decision-making systems.

## 🌟 Features

- **Governance Framework**: Proven Westminster-style separation of powers
- **Four Core Agents**: Strategic (Planner), Implementation (Executor), Quality (Evaluator), Oversight (Overwatch)
- **Organizational Processes**: Decision-making, review cycles, escalation, and crisis management
- **Agent Communication**: Structured messaging with accountability oversight
- **MCP Integration**: External system connectivity with audit trails
- **FastAPI**: Modern async API with comprehensive documentation
- **Pydantic AI**: Type-safe agent implementation with structured outputs

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/triad-model.git
cd triad-model

# Create virtual environment (required on macOS)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
# Edit .env with your API keys
```

### Run the Application

```bash
# Check configuration
python scripts/start.py --check-config

# Start development server
python scripts/start.py

# Or use make
make run
```

Access the API documentation at http://localhost:8000/docs

## 🏗️ Architecture

```
Triad Model
├── Planner Agent (Legislative Branch)
│   ├── Policy creation and planning
│   ├── Workflow design
│   └── Legislative review
├── Executor Agent (Executive Branch)
│   ├── Implementation and execution
│   ├── Resource management
│   └── Administrative actions
├── Evaluator Agent (Judicial Branch)
│   ├── Constitutional review
│   ├── Compliance evaluation
│   └── Judicial decisions
└── Overwatch Agent (Crown)
    ├── Constitutional oversight
    ├── Crisis management
    └── System monitoring
```

## 📚 Documentation

- [Setup Guide](SETUP.md) - Detailed installation instructions
- [Architecture](docs/system/architecture.md) - System design and principles
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)

## 🛠️ Development

```bash
# Run tests
make test

# Check code quality
make lint

# Format code
make format

# Constitutional compliance check
make constitutional-check
```

## 🤝 Contributing

Contributions must maintain constitutional compliance and parliamentary accountability. Please ensure:

1. All tests pass (`make check`)
2. Constitutional compliance is maintained
3. Parliamentary procedures are followed
4. Documentation is updated

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- [Documentation](https://triad-model.readthedocs.io)
- [API Reference](http://localhost:8000/docs)
- [Issues](https://github.com/your-org/triad-model/issues)

---

Built with Pydantic AI, FastAPI, and constitutional principles 🏛️