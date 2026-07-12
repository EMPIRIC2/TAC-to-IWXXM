"""Package import smoke for tac2iwxxm (T1.1 / TC-F6-M001)."""

from __future__ import annotations

import tac2iwxxm


def test_package_version_is_set() -> None:
    assert tac2iwxxm.__version__
