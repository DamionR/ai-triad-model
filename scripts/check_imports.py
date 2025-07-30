#!/usr/bin/env python3
"""
Check all imports in the Triad Model system.

This script validates that all modules can be imported successfully
and reports any import errors.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Track results
successful_imports = []
failed_imports = []

def try_import(module_name: str) -> bool:
    """Try to import a module and report success/failure."""
    try:
        # Use __import__ to dynamically import modules
        __import__(module_name)
        successful_imports.append(module_name)
        print(f"✅ {module_name}")
        return True
    except ImportError as e:
        failed_imports.append((module_name, str(e)))
        print(f"❌ {module_name}: {e}")
        return False
    except Exception as e:
        failed_imports.append((module_name, f"Unexpected error: {e}"))
        print(f"❌ {module_name}: Unexpected error: {e}")
        return False

# List of all modules to check
modules_to_check = [
    # Core modules
    "triad",
    "triad.core",
    "triad.core.config",
    "triad.core.constitutional",
    "triad.core.dependencies",
    
    # Agent modules
    "triad.agents",
    "triad.agents.base",
    "triad.agents.planner",
    "triad.agents.executor",
    "triad.agents.evaluator",
    "triad.agents.overwatch",
    
    # Parliamentary modules
    "triad.parliamentary",
    "triad.parliamentary.procedures",
    "triad.parliamentary.question_period",
    "triad.parliamentary.crisis",
    "triad.parliamentary.crown",
    
    # A2A communication modules
    "triad.a2a",
    "triad.a2a.broker",
    "triad.a2a.client",
    "triad.a2a.models",
    "triad.a2a.storage",
    
    # MCP modules
    "triad.mcp",
    "triad.mcp.client",
    "triad.mcp.adapters",
    "triad.mcp.servers",
    "triad.mcp.tools",
    
    # API modules
    "triad.api",
    "triad.api.main",
    "triad.api.models",
    "triad.api.routes",
    "triad.api.routes.agents",
    "triad.api.routes.health",
    "triad.api.routes.parliamentary",
    
    # Database modules
    "triad.database",
    "triad.database.models",
    
    # Model modules
    "triad.models",
    "triad.models.agents",
    "triad.models.tasks",
    "triad.models.workflows",
    "triad.models.parliamentary",
]

print("🔍 Checking imports for Triad Model...\n")

# Check each module
for module in modules_to_check:
    try_import(module)

print(f"\n📊 Import Check Summary:")
print(f"   ✅ Successful imports: {len(successful_imports)}")
print(f"   ❌ Failed imports: {len(failed_imports)}")

if failed_imports:
    print(f"\n❌ Failed imports details:")
    for module, error in failed_imports:
        print(f"   - {module}: {error}")
    
    # Analyze common issues
    missing_deps = set()
    for module, error in failed_imports:
        if "No module named" in error:
            # Extract missing module name
            parts = error.split("'")
            if len(parts) >= 2:
                missing_dep = parts[1].split('.')[0]
                if missing_dep not in ['triad']:  # Exclude our own modules
                    missing_deps.add(missing_dep)
    
    if missing_deps:
        print(f"\n📦 Missing dependencies detected:")
        for dep in sorted(missing_deps):
            print(f"   - {dep}")
        print("\n💡 To install missing dependencies, create a virtual environment and run:")
        print("   python3 -m venv venv")
        print("   source venv/bin/activate")
        print("   pip install -r requirements.txt")
else:
    print("\n✅ All imports successful! The Triad Model is ready to use.")
    print("\n🚀 To start the server, run:")
    print("   python scripts/start.py")

# Exit with appropriate code
sys.exit(1 if failed_imports else 0)