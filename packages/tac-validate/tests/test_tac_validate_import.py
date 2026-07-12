"""Package import smoke for tac-validate (T1.1 / TC-F6-M001)."""

from __future__ import annotations

import tac_validate


def test_package_version_is_set() -> None:
    assert tac_validate.__version__
