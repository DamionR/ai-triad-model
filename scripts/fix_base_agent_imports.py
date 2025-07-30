#!/usr/bin/env python3
"""Fix BaseAgent imports in role modules."""

import os
import re
from pathlib import Path

def fix_base_agent_imports(file_path):
    """Fix BaseAgent imports in a Python file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Replace the import
    content = re.sub(
        r'from \.base import BaseAgent',
        'from ..core.base import BaseAgent',
        content
    )
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Main function to fix imports in role files."""
    project_root = Path(__file__).parent.parent
    roles_dir = project_root / 'triad' / 'agents' / 'roles'
    
    fixed_files = []
    
    # Walk through all Python files in roles directory
    for file in roles_dir.glob('*.py'):
        if file.name != '__init__.py':
            if fix_base_agent_imports(file):
                fixed_files.append(file)
                print(f"Fixed imports in: {file.relative_to(project_root)}")
    
    print(f"\nTotal files fixed: {len(fixed_files)}")

if __name__ == "__main__":
    main()