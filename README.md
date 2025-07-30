# AI Triad Model 🤖

A structured multi-agent AI framework with built-in oversight and transparent decision-making. Four specialized agents work together using proven architectural patterns for reliable AI coordination.

## 🌟 Features

- **Four-Agent Architecture**: Planner, Executor, Evaluator, and Oversight agents
- **Structured Coordination**: Clear separation of responsibilities and systematic workflows  
- **Built-in Oversight**: Quality assurance and compliance checking at every step
- **Transparent Processes**: Complete audit trails and decision logging
- **Modern Stack**: Built with Pydantic AI, FastAPI, and Prisma
- **Easy Integration**: Simple Python SDK with comprehensive documentation

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/DamionR/ai-triad-model.git
cd ai-triad-model

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys
```

### Run the Application

```bash
# Start the development server
python scripts/start.py

# Or use make
make run
```

Access the API at http://localhost:8000/docs

## 🏗️ Architecture

```
AI Triad Model
├── Planner Agent
│   ├── Strategic planning
│   ├── Workflow design
│   └── Task coordination
├── Executor Agent  
│   ├── Plan implementation
│   ├── Resource management
│   └── Operational tasks
├── Evaluator Agent
│   ├── Quality review
│   ├── Compliance checking
│   └── Performance evaluation
└── Oversight Agent
    ├── System monitoring
    ├── Crisis management
    └── Final approval
```

## 💡 Basic Usage

```python
from triad import TriadFramework

# Initialize the framework
framework = TriadFramework()

# Process a request through all four agents
result = await framework.process_request(
    request="Analyze market trends for Q4 strategy",
    require_consensus=True
)

print(result.response)
print(result.audit_trail)
```

## 📚 Documentation

- [Setup Guide](SETUP.md) - Detailed installation and configuration
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Architecture Overview](docs/MULTI_AGENT_ARCHITECTURE.md) - System design
- [Tools Integration](docs/TOOLS_AND_MCP_GUIDE.md) - MCP and external tools

## 🛠️ Development

```bash
# Run tests
make test

# Check code quality  
make lint

# Format code
make format

# Run full checks
make check
```

## 🌐 Landing Page

Check out the landing page at: https://damionr.github.io/ai-triad-model/

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and checks: `make check`
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- [Landing Page](https://damionr.github.io/ai-triad-model/)
- [GitHub Repository](https://github.com/DamionR/ai-triad-model)
- [Issues](https://github.com/DamionR/ai-triad-model/issues)

---

Built with Pydantic AI and modern Python frameworks 🐍