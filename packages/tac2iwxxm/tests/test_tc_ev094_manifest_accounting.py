"""TC-EV094-007 — aggregate manifest accounting for thin/compat deepen packs.

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: tests §TC-EV094]
"""

from __future__ import annotations

import json
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles"

EXPECTED_COUNTS = {
    "UK_METOFFICE": {"active": 3, "attributed": 2, "synthetic": 1, "parse_only": 0},
    "BR_DECEA": {"active": 5, "attributed": 2, "synthetic": 4, "parse_only": 1},
    "KR_KMA": {"active": 5, "attributed": 2, "synthetic": 3, "parse_only": 0},
    "JP_JMA": {"active": 5, "attributed": 2, "synthetic": 3, "parse_only": 0},
    "IN_IMD": {"active": 4, "attributed": 2, "synthetic": 2, "parse_only": 0},
    "HK_HKO": {"active": 5, "attributed": 2, "synthetic": 3, "parse_only": 0},
}


def _load_manifest(profile_id: str) -> dict[str, object]:
    return json.loads((FIXTURES / profile_id / "manifest.json").read_text(encoding="utf-8"))


def _summarize_counts(profile_id: str) -> dict[str, int]:
    cases = _load_manifest(profile_id)["cases"]
    assert isinstance(cases, list)
    return {
        "active": sum(1 for case in cases if str(case.get("status", "active")) == "active"),
        "attributed": sum(1 for case in cases if bool(case.get("source_url"))),
        "synthetic": sum(1 for case in cases if case.get("source_kind") == "synthetic_ev089"),
        "parse_only": sum(1 for case in cases if case.get("status") == "parse_only"),
    }


def test_tc_ev094_007_manifest_accounting_by_profile() -> None:
    """EV-094 fixture manifests expose explicit per-profile quality counts."""
    observed = {profile_id: _summarize_counts(profile_id) for profile_id in EXPECTED_COUNTS}
    assert observed == EXPECTED_COUNTS


def test_tc_ev094_008_manifest_accounting_totals() -> None:
    """Aggregate EV-094 totals stay stable across the shipped thin/compat deepen set."""
    totals = {"active": 0, "attributed": 0, "synthetic": 0, "parse_only": 0}
    for profile_id in EXPECTED_COUNTS:
        for key, value in _summarize_counts(profile_id).items():
            totals[key] += value

    assert totals == {
        "active": 27,
        "attributed": 12,
        "synthetic": 16,
        "parse_only": 1,
    }
