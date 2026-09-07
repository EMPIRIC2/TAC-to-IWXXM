"""Regression: production login fails when only legacy Supabase JWT keys are configured.

F21 / ADR-031 (S023 / EV-017): operator Auth / login dual path removed.
Historical assertions live in git history; module skipped for ci-prepush.
"""

from __future__ import annotations

import pytest

pytest.skip(
    "F21/ADR-031: operator Auth / DISABLE_AUTH dual path removed - bug N/A",
    allow_module_level=True,
)
