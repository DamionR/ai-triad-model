#!/usr/bin/env python3
"""Fix relative imports to absolute imports in the Triad project."""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix relative imports in a Python file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Store original content for comparison
    original_content = content
    
    # Pattern to match relative imports starting with ..
    patterns = [
        (r'from \.\.core\.dependencies', 'from triad.core.dependencies'),
        (r'from \.\.core\.constitutional', 'from triad.core.constitutional'),
        (r'from \.\.core\.message_history', 'from triad.core.messaging.message_history'),
        (r'from \.\.database\.models', 'from triad.database.models'),
        (r'from \.\.models', 'from triad.api.models'),
        (r'from \.\.\.core\.dependencies', 'from triad.core.dependencies'),
        (r'from \.\.\.core\.constitutional', 'from triad.core.constitutional'),
        (r'from \.\.\.core\.message_history', 'from triad.core.messaging.message_history'),
        (r'from \.\.\.parliamentary\.procedures', 'from triad.parliamentary.procedures'),
        (r'from \.\.\.parliamentary\.question_period', 'from triad.parliamentary.question_period'),
        (r'from \.\.\.agents\.planner', 'from triad.agents.roles.planner'),
        (r'from \.\.\.agents\.executor', 'from triad.agents.roles.executor'),
        (r'from \.\.\.agents\.evaluator', 'from triad.agents.roles.evaluator'),
        (r'from \.\.\.agents\.overwatch', 'from triad.agents.roles.overwatch'),
        (r'from \.\.models\.workflow', 'from triad.models.workflow'),
        (r'from \.\.models\.execution', 'from triad.models.execution'),
        (r'from \.\.models\.monitoring', 'from triad.models.monitoring'),
        (r'from \.\.models\.validation', 'from triad.models.validation'),
        (r'from \.\.agents\.core\.dependencies', 'from triad.core.dependencies'),
        (r'from \.\.agents\.core\.constitutional', 'from triad.core.constitutional'),
    ]
    
    # Apply all replacements
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Check if any changes were made
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
    
    # Walk through all Python files in the triad directory
    for root, dirs, files in os.walk(triad_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                if fix_imports_in_file(file_path):
                    fixed_files.append(file_path)
                    print(f"Fixed imports in: {file_path.relative_to(project_root)}")
    
    print(f"\nTotal files fixed: {len(fixed_files)}")

if __name__ == "__main__":
    main()