#!/usr/bin/env python3
"""
Find unused imports in Python files.

This script identifies imports that are declared but never used.
"""

import ast
import sys
from pathlib import Path
from typing import Set, List, Tuple, Dict

class UnusedImportsFinder(ast.NodeVisitor):
    """AST visitor to find unused imports."""
    
    def __init__(self):
        self.imports: Dict[str, ast.AST] = {}
        self.used_names: Set[str] = set()
        self.in_import = False
        
    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statements."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports[name] = node
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from...import statements."""
        for alias in node.names:
            if alias.name != '*':
                name = alias.asname if alias.asname else alias.name
                self.imports[name] = node
        self.generic_visit(node)
        
    def visit_Name(self, node: ast.Name) -> None:
        """Visit name references."""
        if not self.in_import:
            self.used_names.add(node.id)
        self.generic_visit(node)
        
    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Visit attribute access."""
        if isinstance(node.value, ast.Name):
            self.used_names.add(node.value.id)
        self.generic_visit(node)
        
    def get_unused_imports(self) -> List[Tuple[str, int]]:
        """Get list of unused imports with line numbers."""
        unused = []
        for name, node in self.imports.items():
            if name not in self.used_names:
                # Special cases that might be used indirectly
                special_cases = {
                    '__future__', 'annotations', 'typing_extensions',
                    # Common side-effect imports
                    'logging', 'warnings', 'sys.path',
                    # Type checking imports might be used in string annotations
                    'TYPE_CHECKING'
                }
                
                if name not in special_cases and not name.startswith('_'):
                    unused.append((name, node.lineno))
        
        return sorted(unused, key=lambda x: x[1])

def check_file(file_path: Path) -> List[Tuple[str, int]]:
    """Check a single file for unused imports."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(file_path))
        finder = UnusedImportsFinder()
        finder.visit(tree)
        
        return finder.get_unused_imports()
    except Exception as e:
        print(f"Error checking {file_path}: {e}")
        return []

def main():
    """Main function."""
    project_root = Path(__file__).parent.parent
    triad_dir = project_root / "triad"
    scripts_dir = project_root / "scripts"
    
    print("🔍 Finding unused imports in Triad Model...\n")
    
    # Find all Python files
    python_files = []
    python_files.extend(triad_dir.glob("**/*.py"))
    python_files.extend(scripts_dir.glob("*.py"))
    
    # Track files with unused imports
    files_with_unused = []
    total_unused = 0
    
    # Check each file
    for file_path in sorted(python_files):
        if "__pycache__" in str(file_path):
            continue
            
        relative_path = file_path.relative_to(project_root)
        unused_imports = check_file(file_path)
        
        if unused_imports:
            files_with_unused.append((relative_path, unused_imports))
            total_unused += len(unused_imports)
            
            print(f"📄 {relative_path}")
            for name, line in unused_imports:
                print(f"   Line {line}: '{name}' is imported but never used")
            print()
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Files checked: {len(list(python_files))}")
    print(f"   Files with unused imports: {len(files_with_unused)}")
    print(f"   Total unused imports: {total_unused}")
    
    if total_unused > 0:
        print(f"\n💡 To fix: Remove the unused imports from the files listed above")
        return 1
    else:
        print(f"\n✅ No unused imports found!")
        return 0

if __name__ == "__main__":
    sys.exit(main())