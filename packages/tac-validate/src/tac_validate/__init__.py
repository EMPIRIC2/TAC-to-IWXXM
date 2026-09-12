"""TAC parse gate and business-rule pack (F6 lint).

Call :func:`tac_validate.api.lint` for product-scoped TAC lint reports. Issue
codes live in the registry (see ``docs/engineering/docstrings.md`` for the
documentation bar).
"""

from __future__ import annotations

from tac_validate.api import lint
from tac_validate.models import Fix, Issue, LintReport
from tac_validate.products import PRODUCTS

__version__ = "2026.9.10"

__all__ = ["PRODUCTS", "Fix", "Issue", "LintReport", "__version__", "lint"]
