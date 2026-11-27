"""Root test fixtures for connectivity and workspace smoke tests."""

from __future__ import annotations

import os

# NFR-007: dedicated api-key tests enable enforcement; keep root suites off.
os.environ.setdefault("API_KEY_REQUIRED", "false")
os.environ.setdefault("DEMO_API_KEY", "test-demo-api-key")

pytest_plugins: list[str] = []
