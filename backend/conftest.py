"""Backend-specific pytest configuration and fixtures.

This file ensures backend src is importable in tests.
All other pytest configuration is in pyproject.toml.
"""
import pathlib
import sys

# Ensure backend src is always importable in tests
BACKEND_DIR = pathlib.Path(__file__).resolve().parent
BACKEND_SRC = BACKEND_DIR / "src"

if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))
