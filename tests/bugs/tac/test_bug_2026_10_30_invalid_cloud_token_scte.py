"""BUG-2026-10-30 — INVALID_CLOUD_TOKEN must not fire on station SCTE.

R4 YAML ``token_scan`` select used ``SCT`` as a prefix, so ICAO ``SCTE``
matched as a cloud candidate and failed ``ok``. Legacy ``_CLOUD_START`` /
``_CLOUD_LIKE`` used the same prefix shape for ``_cloud_candidate_tokens``.

Live-map full-world probe 2026-10-30: 2 places (METAR+SPECI SCTE), pass=true.
Ticket: #1478. [Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac_validate import lint
from tac_validate.product_rules_pkg._common import _CLOUD_LIKE, _CLOUD_START

_METAR_SCTE = "METAR SCTE 302100Z 14011KT 110V170 CAVOK 16/08 Q1014 NOSIG"
_SPECI_SCTE = "SPECI SCTE 300923Z 20006KT 9999 FEW020 SCT035 10/09 Q1016 NOSIG"
_MALFORMED_CLOUD = "METAR KJFK 231751Z 18012KT 10SM FEW40 15/07 A3005="


@pytest.mark.parametrize(
    ("tac", "product"),
    [
        (_METAR_SCTE, "METAR"),
        (_SPECI_SCTE, "SPECI"),
    ],
    ids=["metar_scte", "speci_scte"],
)
def test_bug_2026_10_30_scte_station_not_invalid_cloud_token(
    tac: str, product: str
) -> None:
    codes = {i.code for i in lint(tac, product=product).issues}
    assert "INVALID_CLOUD_TOKEN" not in codes


@pytest.mark.parametrize(
    ("tac", "product"),
    [
        (_MALFORMED_CLOUD, "METAR"),
        ("SPECI KJFK 231751Z 18012KT 10SM BKN40 15/07 A3005=", "SPECI"),
    ],
    ids=["metar_few40", "speci_bkn40"],
)
def test_bug_2026_10_30_malformed_cloud_still_invalid(tac: str, product: str) -> None:
    codes = {i.code for i in lint(tac, product=product).issues}
    assert "INVALID_CLOUD_TOKEN" in codes


@pytest.mark.parametrize(
    ("token", "expect_match"),
    [
        ("SCTE", False),
        ("OVCE", False),
        ("SCT035", True),
        ("FEW020", True),
        ("NSC", True),
    ],
    ids=["scte", "ovce", "sct035", "few020", "nsc"],
)
def test_bug_2026_10_30_cloud_start_like_reject_icao_prefix(
    token: str, expect_match: bool
) -> None:
    """Validation: Python cloud selectors match R4 YAML ``(?![A-Z])`` guard."""
    assert bool(_CLOUD_START.match(token)) is expect_match
    assert bool(_CLOUD_LIKE.match(token)) is expect_match
