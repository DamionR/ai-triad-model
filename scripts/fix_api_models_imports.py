#!/usr/bin/env python3
"""Fix api.models imports to models imports."""

import os
import re
from pathlib import Path

def fix_api_models_imports(file_path):
    """Fix api.models imports in a Python file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Replace the imports
    content = re.sub(
        r'from triad\.api\.models\.',
        'from triad.models.',
        content
    )
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Main function to fix imports."""
    project_root = Path(__file__).parent.parent
    
    fixed_files = []
    
    # Walk through all Python files
    for root, dirs, files in os.walk(project_root / 'triad'):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                if fix_api_models_imports(file_path):
                    fixed_files.append(file_path)
                    print(f"Fixed imports in: {file_path.relative_to(project_root)}")
    
    print(f"\nTotal files fixed: {len(fixed_files)}")

if __name__ == "__main__":
    main()