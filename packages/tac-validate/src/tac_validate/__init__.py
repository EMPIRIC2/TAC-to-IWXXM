"""TAC parse gate and business-rule pack (F6 lint)."""

from __future__ import annotations

from tac_validate.api import lint
from tac_validate.models import Fix, Issue, LintReport
from tac_validate.products import PRODUCTS

__version__ = "0.1.3"

__all__ = ["PRODUCTS", "Fix", "Issue", "LintReport", "__version__", "lint"]
