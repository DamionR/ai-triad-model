#!/usr/bin/env python3
"""
Check syntax errors in all Python files.

This script validates Python syntax without requiring dependencies
to be installed.
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

def check_file_syntax(file_path: Path) -> Tuple[bool, str]:
    """Check if a Python file has valid syntax."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse the file
        ast.parse(content, filename=str(file_path))
        return True, "OK"
    except SyntaxError as e:
        return False, f"SyntaxError at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def find_python_files(root_dir: Path) -> List[Path]:
    """Find all Python files in the project."""
    return list(root_dir.glob("**/*.py"))

def main():
    """Main function to check all Python files."""
    project_root = Path(__file__).parent.parent
    triad_dir = project_root / "triad"
    scripts_dir = project_root / "scripts"
    
    print("🔍 Checking Python syntax in Triad Model...\n")
    
    # Find all Python files
    python_files = []
    python_files.extend(find_python_files(triad_dir))
    python_files.extend(find_python_files(scripts_dir))
    
    # Track results
    syntax_errors = []
    checked_files = 0
    
    # Check each file
    for file_path in sorted(python_files):
        if "__pycache__" in str(file_path):
            continue
            
        relative_path = file_path.relative_to(project_root)
        is_valid, message = check_file_syntax(file_path)
        checked_files += 1
        
        if is_valid:
            print(f"✅ {relative_path}")
        else:
            print(f"❌ {relative_path}: {message}")
            syntax_errors.append((relative_path, message))
    
    # Summary
    print(f"\n📊 Syntax Check Summary:")
    print(f"   Files checked: {checked_files}")
    print(f"   ✅ Valid syntax: {checked_files - len(syntax_errors)}")
    print(f"   ❌ Syntax errors: {len(syntax_errors)}")
    
    if syntax_errors:
        print("\n❌ Files with syntax errors:")
        for file_path, error in syntax_errors:
            print(f"   - {file_path}: {error}")
        return 1
    else:
        print("\n✅ All files have valid Python syntax!")
        return 0

if __name__ == "__main__":
    sys.exit(main())