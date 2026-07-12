"""Package import smoke for iwxxm-validate (T1.1 / TC-F6-M001)."""

from __future__ import annotations

import iwxxm_validate


def test_package_version_is_set() -> None:
    assert iwxxm_validate.__version__
