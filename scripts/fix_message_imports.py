#!/usr/bin/env python3
"""Fix Message imports to use correct pydantic_ai message types."""

import os
import re
from pathlib import Path

def fix_message_imports(file_path):
    """Fix Message imports in a Python file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Replace Message with ModelMessage
    content = re.sub(
        r'from pydantic_ai\.messages import ([^)]+)?Message([^a-zA-Z])',
        r'from pydantic_ai.messages import \1ModelMessage\2',
        content
    )
    
    # Replace UserMessage with UserPromptPart
    content = re.sub(
        r'UserMessage',
        'UserPromptPart',
        content
    )
    
    # Replace SystemMessage with SystemPromptPart
    content = re.sub(
        r'SystemMessage',
        'SystemPromptPart',
        content
    )
    
    # Replace UserPrompt with UserPromptPart
    content = re.sub(
        r'UserPrompt(?!Part)',
        'UserPromptPart',
        content
    )
    
    # Replace SystemPrompt with SystemPromptPart
    content = re.sub(
        r'SystemPrompt(?!Part)',
        'SystemPromptPart',
        content
    )
    
    # Fix Message type annotations
    content = re.sub(
        r': Message(?![a-zA-Z])',
        ': ModelMessage',
        content
    )
    
    content = re.sub(
        r'\[Message\]',
        '[ModelMessage]',
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
                if fix_message_imports(file_path):
                    fixed_files.append(file_path)
                    print(f"Fixed imports in: {file_path.relative_to(project_root)}")
    
    print(f"\nTotal files fixed: {len(fixed_files)}")

if __name__ == "__main__":
    main()