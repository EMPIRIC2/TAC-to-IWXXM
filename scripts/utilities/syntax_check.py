#!/usr/bin/env python3
"""
Syntax checker for Python files.

Usage:
    python syntax_check.py <file>           # Check single file
    python syntax_check.py <directory>      # Check all .py files in directory
    python syntax_check.py --all            # Check all Python files in project
"""

import sys
import py_compile
from pathlib import Path
from typing import List, Tuple


def check_syntax(file_path: Path) -> Tuple[bool, str]:
    """
    Check syntax of a Python file.
    
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        py_compile.compile(str(file_path), doraise=True)
        return True, ""
    except py_compile.PyCompileError as e:
        return False, str(e)


def find_python_files(path: Path) -> List[Path]:
    """Find all Python files in a directory recursively."""
    if path.is_file():
        return [path] if path.suffix == '.py' else []
    
    return list(path.rglob('*.py'))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    arg = sys.argv[1]
    
    # Determine files to check
    if arg == '--all':
        project_root = Path(__file__).parent.parent.parent
        files = []
        for subdir in ['backend', 'auth', 'frontend', 'GIFTs', 'scripts']:
            subpath = project_root / subdir
            if subpath.exists():
                files.extend(find_python_files(subpath))
    else:
        path = Path(arg)
        if not path.exists():
            print(f"Error: Path '{arg}' does not exist")
            sys.exit(1)
        files = find_python_files(path)
    
    if not files:
        print("No Python files found to check")
        sys.exit(0)
    
    # Check all files
    errors = []
    checked = 0
    
    print(f"Checking {len(files)} Python file(s)...")
    
    for file_path in sorted(files):
        success, error = check_syntax(file_path)
        checked += 1
        
        # Get relative path safely
        try:
            display_path = file_path.relative_to(Path.cwd())
        except ValueError:
            display_path = file_path
        
        if success:
            print(f"✓ {display_path}")
        else:
            print(f"✗ {display_path}")
            errors.append((file_path, error))
    
    # Summary
    print(f"\n{'='*70}")
    print(f"Checked: {checked} files")
    print(f"Passed:  {checked - len(errors)} files")
    print(f"Failed:  {len(errors)} files")
    
    if errors:
        print(f"\n{'='*70}")
        print("SYNTAX ERRORS:")
        print('='*70)
        for file_path, error in errors:
            print(f"\n{file_path}:")
            print(f"  {error}")
        sys.exit(1)
    else:
        print("\n✓ All files passed syntax check")
        sys.exit(0)


if __name__ == '__main__':
    main()
