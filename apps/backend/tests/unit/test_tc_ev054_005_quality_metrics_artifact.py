"""TC-EV054-005 — product summary counts match precomputed quality-metrics artifact."""

from __future__ import annotations

from collections import defaultdict

import pytest

from quality_metrics_store import (
    QualityMetricsArtifactMissing,
    clear_corpus_metrics_cache,
    get_detail,
    list_file_rows,
    load_corpus_metrics,
)

# Golden stem set — stable registered passers expected in inventory.
_GOLDEN_STEMS = (
    "metar-A3-1",
    "speci-A3-2",
    "taf-A5-1",
    "sigmet-A6-1a-TS",
)


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    clear_corpus_metrics_cache()
    yield
    clear_corpus_metrics_cache()


def test_tc_ev054_005_artifact_loads_and_summaries_match_files() -> None:
    doc = load_corpus_metrics()
    assert doc["iwxxm_pin"] == "2025-2"
    assert "generated_at" in doc
    assert len(doc["files"]) == 18
    assert len(doc["details"]) == 18

    # Recompute summaries from file rows — must match committed summaries.
    buckets: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "match_pass": 0,
            "match_fail": 0,
            "residual_nonempty": 0,
            "lint_fail": 0,
            "validate_fail": 0,
            "deferred_gaps": 0,
        }
    )
    for row in doc["files"]:
        b = buckets[row["product"]]
        if row["deferred"]:
            b["deferred_gaps"] += 1
            continue
        if row["match_status"] == "equal":
            b["match_pass"] += 1
        else:
            b["match_fail"] += 1
        if row["residual_count"] > 0:
            b["residual_nonempty"] += 1
        if row["lint_error_count"] > 0:
            b["lint_fail"] += 1
        if row["validate_error_count"] > 0:
            b["validate_fail"] += 1

    by_product = {s["product"]: s for s in doc["summaries"]}
    assert set(by_product) == set(buckets)
    for product, expected in buckets.items():
        got = by_product[product]
        for key, value in expected.items():
            assert got[key] == value, (product, key, got[key], value)


def test_tc_ev054_005_golden_stems_have_detail_and_metar_equal() -> None:
    doc = load_corpus_metrics()
    for stem in _GOLDEN_STEMS:
        detail = get_detail(doc, stem)
        assert detail is not None, stem
        assert detail["deferred"] is False
        assert detail["tac"]
        assert detail["official_xml"]
        assert detail["converted_xml"]
        assert "match_status" in detail

    metar = get_detail(doc, "metar-A3-1")
    assert metar is not None
    assert metar["match_status"] == "equal"
    assert metar["product"] == "metar"

    metar_rows = list_file_rows(doc, product="metar")
    assert any(r["stem"] == "metar-A3-1" for r in metar_rows)
    assert any(r["deferred"] for r in metar_rows)  # metar-NIL-collect


def test_tc_ev054_005_missing_artifact_raises(tmp_path) -> None:
    missing = tmp_path / "nope.json"
    with pytest.raises(QualityMetricsArtifactMissing):
        load_corpus_metrics(str(missing))
