"""Lint catalog products must stay aligned with convert allowlist (lintable).

[Corpus: product §F36] [Corpus: tests]
"""

from __future__ import annotations

from tac2iwxxm.convert_allowlist import products_for
from tac_validate.lint_profile_catalog import load_lint_profiles


def test_lint_products_subset_of_convert_allowlist() -> None:
    """Every lint product for a profile must be convert-allowed (when listed)."""
    rows = load_lint_profiles()
    for profile_id, spec in rows.items():
        allowed = products_for(profile_id)
        if allowed is None:
            continue
        allowed_u = {item.upper() for item in allowed}
        missing = sorted(spec.products - allowed_u)
        assert not missing, f"{profile_id} lints {missing} but convert allowlist is {sorted(allowed_u)}"
