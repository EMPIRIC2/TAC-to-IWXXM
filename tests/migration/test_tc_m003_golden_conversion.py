"""TC-M003 deprecated after F6 cutover - gifts goldens archived via tac2iwxxm annex3 pack.

Historical gifts parity (TC-M003) is superseded by TC-F6-020/021 and TC-F6-022.
[Corpus: tests] — assert successor goldens exist; do not skip.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.migration

ROOT = Path(__file__).resolve().parents[2]
ANNEX3_GOLDEN = (
    ROOT / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "annex3_golden"
)


def test_tc_m003_superseded_by_tac2iwxxm_goldens() -> None:
    """Cutover: gifts baseline lives under tac2iwxxm annex3_golden fixtures."""
    assert ANNEX3_GOLDEN.is_dir(), (
        "TC-M003 successor goldens missing — expected "
        "packages/tac2iwxxm/tests/fixtures/annex3_golden (TC-F6-020/021/003)"
    )
    goldens = list(ANNEX3_GOLDEN.glob("*.golden.xml")) + list(
        ANNEX3_GOLDEN.glob("*.xml")
    )
    assert goldens, "annex3_golden must contain at least one IWXXM fixture"
