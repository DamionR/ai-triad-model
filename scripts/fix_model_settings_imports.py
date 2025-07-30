#!/usr/bin/env python3
"""Fix ModelSettings imports in the project."""

import os
import re
from pathlib import Path

def fix_model_settings_imports(file_path):
    """Fix ModelSettings imports in a Python file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Replace the import
    content = re.sub(
        r'from pydantic_ai\.settings import ModelSettings',
        'from pydantic_ai.models import ModelSettings',
        content
    )
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Main function to fix imports in all Python files."""
    project_root = Path(__file__).parent.parent
    triad_dir = project_root / 'triad'
    
    fixed_files = []
    
    # Walk through all Python files
    for root, dirs, files in os.walk(triad_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                if fix_model_settings_imports(file_path):
                    fixed_files.append(file_path)
                    print(f"Fixed imports in: {file_path.relative_to(project_root)}")
    
    print(f"\nTotal files fixed: {len(fixed_files)}")

if __name__ == "__main__":
    main()