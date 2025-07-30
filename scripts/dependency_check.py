#!/usr/bin/env python3
"""
Dependency and Import Health Check

Comprehensive check for dependencies, imports, and code quality issues.
"""

import sys
from pathlib import PathAlso 
from typing import List, Dict, Tuple

def check_python_version() -> Tuple[bool, str]:
    """Check if Python version meets requirements."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        return True, f"{version.major}.{version.minor}.{version.micro}"
    return False, f"{version.major}.{version.minor}.{version.micro} (requires 3.11+)"

def check_virtual_env() -> Tuple[bool, str]:
    """Check if running in a virtual environment."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return True, sys.prefix
    return False, "Not in virtual environment"

def check_required_files() -> List[Tuple[str, bool]]:
    """Check if required files exist."""
    project_root = Path(__file__).parent.parent
    required_files = [
        "pyproject.toml",
        "requirements.txt",
        "README.md",
        "SETUP.md",
        ".env.example",
        "Makefile",
        "config/default.yaml",
        "triad/__init__.py",
        "scripts/start.py"
    ]
    
    results = []
    for file in required_files:
        file_path = project_root / file
        results.append((file, file_path.exists()))
    
    return results

def check_dependencies_installed() -> Tuple[bool, List[str]]:
    """Check if key dependencies are installed."""
    key_deps = [
        "fastapi",
        "pydantic",
        "pydantic_ai",
        "logfire",
        "httpx",
        "sqlalchemy",
        "alembic",
        "uvicorn"
    ]
    
    missing = []
    for dep in key_deps:
        try:
            __import__(dep.replace("-", "_"))
        except ImportError:
            missing.append(dep)
    
    return len(missing) == 0, missing

def check_code_issues() -> Dict[str, int]:
    """Check for common code issues."""
    project_root = Path(__file__).parent.parent
    triad_dir = project_root / "triad"
    
    issues = {
        "deprecated_utcnow": 0,
        "missing_timezone": 0,
        "unused_imports": 0,
        "long_lines": 0
    }
    
    # Check for deprecated datetime.utcnow()
    for py_file in triad_dir.glob("**/*.py"):
        if "__pycache__" in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
                
                # Count deprecated utcnow
                issues["deprecated_utcnow"] += content.count("datetime.utcnow()")
                
                # Check for timezone imports
                if "from datetime import" in content and "timezone" not in content:
                    issues["missing_timezone"] += 1
                
                # Check line length
                for line in lines:
                    if len(line) > 120:
                        issues["long_lines"] += 1
                        
        except Exception:
            pass
    
    return issues

def main():
    """Run comprehensive dependency and import checks."""
    print("🔍 Triad Model - Dependency and Import Health Check\n")
    
    # Check Python version
    py_ok, py_version = check_python_version()
    print(f"{'✅' if py_ok else '❌'} Python Version: {py_version}")
    
    # Check virtual environment
    venv_ok, venv_info = check_virtual_env()
    print(f"{'✅' if venv_ok else '⚠️ '} Virtual Environment: {venv_info}")
    
    # Check required files
    print("\n📁 Required Files:")
    files = check_required_files()
    all_files_ok = all(exists for _, exists in files)
    for file, exists in files:
        print(f"   {'✅' if exists else '❌'} {file}")
    
    # Check dependencies
    deps_ok, missing_deps = check_dependencies_installed()
    print(f"\n📦 Dependencies: {'✅ All installed' if deps_ok else '❌ Missing dependencies'}")
    if missing_deps:
        print("   Missing:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n   💡 To install dependencies:")
        print("      python3 -m venv venv")
        print("      source venv/bin/activate")
        print("      pip install -r requirements.txt")
    
    # Check code issues
    print("\n🔧 Code Quality:")
    issues = check_code_issues()
    print(f"   ⚠️  Deprecated datetime.utcnow(): {issues['deprecated_utcnow']} occurrences")
    print(f"   ⚠️  Missing timezone imports: {issues['missing_timezone']} files")
    print(f"   ⚠️  Long lines (>120 chars): {issues['long_lines']} lines")
    
    # Summary and recommendations
    print("\n📊 Summary:")
    
    all_ok = py_ok and all_files_ok and deps_ok
    
    if all_ok:
        print("   ✅ Basic requirements met")
    else:
        print("   ❌ Some requirements not met")
    
    print("\n💡 Recommendations:")
    
    if not venv_ok:
        print("   1. Use a virtual environment to avoid dependency conflicts")
        
    if not deps_ok:
        print("   2. Install missing dependencies (see instructions above)")
        
    if issues["deprecated_utcnow"] > 0:
        print(f"   3. Replace {issues['deprecated_utcnow']} uses of datetime.utcnow() with datetime.now(timezone.utc)")
        
    if not all_ok:
        print("\n⚠️  Fix the issues above before running the application")
    else:
        print("\n✅ Ready to run! Use: python scripts/start.py")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())