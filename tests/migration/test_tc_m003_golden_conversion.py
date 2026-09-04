"""TC-M003 deprecated after F6 cutover - gifts goldens archived via tac2iwxxm annex3 pack.

Historical gifts parity (TC-M003) is superseded by TC-F6-020/021 and TC-F6-022.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.migration


def test_tc_m003_superseded_by_tac2iwxxm_goldens() -> None:
    """Cutover: gifts baseline conversion regression is no longer runnable."""
    pytest.skip(
        "TC-M003 deprecated - use packages/tac2iwxxm annex3/iwxxm_us goldens (TC-F6-020/021/003)"
    )
