"""BUG-2026-10-30 — INVALID_CLOUD_TOKEN must not fire on station SCTE.

R4 YAML ``token_scan`` select used ``SCT`` as a prefix, so ICAO ``SCTE``
matched as a cloud candidate and failed ``ok``.

Live-map full-world probe 2026-10-30: 2 places (METAR+SPECI SCTE), pass=true.
Ticket: #1478. [Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate import lint

_METAR = "METAR SCTE 302100Z 14011KT 110V170 CAVOK 16/08 Q1014 NOSIG"
_SPECI = "SPECI SCTE 300923Z 20006KT 9999 FEW020 SCT035 10/09 Q1016 NOSIG"


def test_bug_2026_10_30_metar_scte_not_invalid_cloud_token() -> None:
    codes = {i.code for i in lint(_METAR, product="METAR").issues}
    assert "INVALID_CLOUD_TOKEN" not in codes


def test_bug_2026_10_30_speci_scte_not_invalid_cloud_token() -> None:
    codes = {i.code for i in lint(_SPECI, product="SPECI").issues}
    assert "INVALID_CLOUD_TOKEN" not in codes


def test_bug_2026_10_30_malformed_cloud_still_invalid() -> None:
    tac = "METAR KJFK 231751Z 18012KT 10SM FEW40 15/07 A3005="
    codes = {i.code for i in lint(tac, product="METAR").issues}
    assert "INVALID_CLOUD_TOKEN" in codes
