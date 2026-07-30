"""TC-EV023-001 / T1.3 — NSC exclusivity lint (NSC_WITH_CLOUD_LAYERS)."""

from __future__ import annotations

from tac_validate import lint
from tac_validate.issue_registry import by_code


def test_tc_ev023_001_registry_nsc_with_cloud_layers() -> None:
    spec = by_code("NSC_WITH_CLOUD_LAYERS")
    assert spec.severity == "warning"
    assert "14.3" in spec.message_template or "exclusivity" in spec.message_template.lower()


def test_tc_ev023_001_nsc_only_no_exclusivity_warning() -> None:
    report = lint("SPECI KJFK 231751Z 18012KT 9999 NSC 15/07 Q1013=", product="SPECI")
    codes = {i.code for i in report.issues}
    assert "NSC_PRESENT" in codes
    assert "NSC_WITH_CLOUD_LAYERS" not in codes


def test_tc_ev023_001_nsc_with_few_emits_warning() -> None:
    report = lint("SPECI KJFK 231751Z 18012KT 9999 NSC FEW015 15/07 Q1013=", product="SPECI")
    hits = [i for i in report.issues if i.code == "NSC_WITH_CLOUD_LAYERS"]
    assert hits
    assert hits[0].severity == "warning"


def test_tc_ev023_001_nsc_base_tempo_few_no_false_positive() -> None:
    """NSC on base + FEW in TEMPO are different groups — not exclusivity."""
    tac = "SPECI KJFK 231751Z 18012KT 9999 NSC 15/07 Q1013 TEMPO FEW015="
    report = lint(tac, product="SPECI")
    assert "NSC_WITH_CLOUD_LAYERS" not in {i.code for i in report.issues}
