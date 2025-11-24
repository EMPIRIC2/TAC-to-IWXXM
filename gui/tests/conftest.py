import sys
from pathlib import Path

# Ensure repository root is on sys.path so `import gui` works when pytest
# is invoked from inside subdirectories or other project areas.
# This avoids ModuleNotFoundError for the gui package when running tests
# from the repo root or another sibling package directory.
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
