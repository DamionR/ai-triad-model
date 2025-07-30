#!/usr/bin/env python3
"""Fix all import issues in the Triad project."""

import os
import re
import ast
from pathlib import Path

def get_exported_names(file_path):
    """Extract exported function and class names from a Python file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        exported_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                exported_names.add(node.name)
            elif isinstance(node, ast.ClassDef):
                exported_names.add(node.name)
        
        return exported_names
    except:
        return set()

def fix_logging_imports(file_path):
    """Fix imports from the logging module."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Check what's actually in logfire_config.py
    logfire_path = Path(__file__).parent.parent / 'triad' / 'core' / 'logging' / 'logfire_config.py'
    available_names = get_exported_names(logfire_path)
    
    # Remove imports that don't exist
    patterns = [
        (r'from \.logging import \([^)]+\)', 'from .logging import (\n    TriadLogfireConfig,\n    get_logfire_config\n)'),
        (r'from \.\.logging import \([^)]+\)', 'from ..logging import (\n    TriadLogfireConfig,\n    get_logfire_config\n)'),
        (r'from \.\.\.core\.logging import \([^)]+\)', 'from ...core.logging import (\n    TriadLogfireConfig,\n    get_logfire_config\n)'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Fix __all__ exports
    if '__all__' in content:
        # Remove non-existent exports from __all__
        content = re.sub(r'"configure_logfire",?\s*', '', content)
        content = re.sub(r'"create_governance_span",?\s*', '', content)
        content = re.sub(r'"create_agent_span",?\s*', '', content)
        content = re.sub(r'"log_governance_event",?\s*', '', content)
        content = re.sub(r'"log_agent_action",?\s*', '', content)
        content = re.sub(r'"log_compliance_check",?\s*', '', content)
        content = re.sub(r'"setup_instrumentation",?\s*', '', content)
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def fix_messaging_imports(file_path):
    """Fix imports from the messaging module."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Fix imports that are incorrectly pointing to message_history
    patterns = [
        (r'from \.\.\.core\.message_history', 'from triad.core.messaging.message_history'),
        (r'from \.\.core\.message_history', 'from triad.core.messaging.message_history'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Remove non-existent exports from __all__
    if '__all__' in content:
        content = re.sub(r'"ConstitutionalMessageValidator",?\s*', '', content)
        content = re.sub(r'"create_message_history_manager",?\s*', '', content)
        content = re.sub(r'"validate_message_constitutional",?\s*', '', content)
        content = re.sub(r'"get_session_history",?\s*', '', content)
        content = re.sub(r'"store_agent_message",?\s*', '', content)
        content = re.sub(r'"clear_session_history",?\s*', '', content)
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def fix_core_imports(file_path):
    """Fix imports in core __init__ files."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Fix logging imports
    if 'from .logging import' in content:
        content = re.sub(
            r'from \.logging import \([^)]+\)',
            '''from .logging import (
    TriadLogfireConfig,
    get_logfire_config
)''',
            content,
            flags=re.DOTALL
        )
    
    # Fix messaging imports
    if 'from .messaging import' in content:
        content = re.sub(
            r'from \.messaging import \([^)]+\)',
            '''from .messaging import (
    MessageRole,
    StoredMessage,
    ConversationSession,
    MessageHistoryManager,
    get_message_history_manager
)''',
            content,
            flags=re.DOTALL
        )
    
    # Fix dependencies imports
    if 'from .dependencies import' in content:
        content = re.sub(
            r'from \.dependencies import \([^)]+\)',
            '''from .dependencies import (
    get_triad_deps,
    TriadDeps
)''',
            content,
            flags=re.DOTALL
        )
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Main function to fix all imports."""
    project_root = Path(__file__).parent.parent
    
    fixed_files = []
    
    # Fix core/__init__.py
    core_init = project_root / 'triad' / 'core' / '__init__.py'
    if fix_core_imports(core_init):
        fixed_files.append(core_init)
        print(f"Fixed imports in: {core_init.relative_to(project_root)}")
    
    # Fix logging/__init__.py
    logging_init = project_root / 'triad' / 'core' / 'logging' / '__init__.py'
    if fix_logging_imports(logging_init):
        fixed_files.append(logging_init)
        print(f"Fixed imports in: {logging_init.relative_to(project_root)}")
    
    # Fix messaging/__init__.py
    messaging_init = project_root / 'triad' / 'core' / 'messaging' / '__init__.py'
    if fix_messaging_imports(messaging_init):
        fixed_files.append(messaging_init)
        print(f"Fixed imports in: {messaging_init.relative_to(project_root)}")
    
    print(f"\nTotal files fixed: {len(fixed_files)}")

if __name__ == "__main__":
    main()