"""TC-F29-002 (loader foundation) / T1.1 — shared YAML/JSON loader + RuleCase schema (S037 / EV-030)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import pytest
import yaml
from tests.quality_matrices.loaders import (
    BUCKETS,
    RuleCase,
    discover_rule_case_files,
    load_rule_cases,
    load_rule_cases_tree,
)

_TESTDATA = Path(__file__).resolve().parent / "testdata"
_SPIKE_YML = _TESTDATA / "lint" / "metar_speci" / "INVALID_VISIBILITY.yml"


def _write_yml(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def test_load_rule_cases_json_parity_with_yaml(tmp_path: Path) -> None:
    yml_cases = load_rule_cases(_SPIKE_YML)
    raw: object = yaml.safe_load(_SPIKE_YML.read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    payload = cast(dict[str, Any], raw)
    json_path = _write_json(tmp_path / "INVALID_VISIBILITY.json", payload)
    json_cases = load_rule_cases(json_path)
    assert len(yml_cases) == len(json_cases) == 20
    assert [c.node_id for c in yml_cases] == [c.node_id for c in json_cases]
    assert [c.status for c in yml_cases] == [c.status for c in json_cases]
    assert [c.tac for c in yml_cases] == [c.tac for c in json_cases]


def test_load_rule_cases_yaml_extension_alias(tmp_path: Path) -> None:
    payload = {
        "rule_id": "INVALID_WIND",
        "engine": "lint",
        "cases": [
            {
                "bucket": "happy",
                "case_id": "01",
                "status": "needs-fixture",
                "meta": {"reason": "schema alias"},
            }
        ],
    }
    path = _write_yml(tmp_path / "INVALID_WIND.yaml", payload)
    cases = load_rule_cases(path)
    assert len(cases) == 1
    assert cases[0].node_id == "INVALID_WIND/happy/01"


def test_load_rule_cases_flat_list_shape(tmp_path: Path) -> None:
    payload = {
        "cases": [
            {
                "rule_id": "metar_cavok",
                "engine": "convert",
                "bucket": "happy",
                "case_id": 1,
                "status": "ready",
                "tac": "METAR KJFK 121251Z 18008KT 10SM CAVOK 22/12 A3012=",
                "expect": {"encode_ok": True},
            }
        ]
    }
    path = _write_json(tmp_path / "flat.json", payload)
    cases = load_rule_cases(path)
    assert cases[0].rule_id == "metar_cavok"
    assert cases[0].engine == "convert"
    assert cases[0].case_id == "01"
    assert cases[0].expect["encode_ok"] is True


@pytest.mark.parametrize(
    "engine,expect",
    [
        ("lint", {"codes": ["INVALID_VISIBILITY"]}),
        ("convert", {"encode_ok": False}),
        (
            "validate",
            {"sch_ids": ["METAR_SPECI.AerodromeHorizontalVisibility-1"]},
        ),
    ],
)
def test_load_rule_cases_all_engines(
    tmp_path: Path, engine: str, expect: dict[str, object]
) -> None:
    payload = {
        "rule_id": "PILOT_RULE",
        "engine": engine,
        "cases": [
            {
                "bucket": "sad",
                "case_id": "01",
                "status": "ready",
                "tac": "METAR KJFK 121251Z 18008KT BADVIS FEW250 22/12 A3012=",
                "expect": expect,
            }
        ],
    }
    path = _write_yml(tmp_path / f"{engine}.yml", payload)
    cases = load_rule_cases(path)
    assert cases[0].engine == engine
    assert cases[0].expect == expect


def test_schema_rejects_unknown_extension(tmp_path: Path) -> None:
    path = tmp_path / "cases.txt"
    path.write_text("rule_id: X\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unsupported"):
        load_rule_cases(path)


def test_schema_rejects_empty_cases(tmp_path: Path) -> None:
    path = _write_yml(
        tmp_path / "empty.yml",
        {"rule_id": "X", "engine": "lint", "cases": []},
    )
    with pytest.raises(ValueError, match="non-empty"):
        load_rule_cases(path)


def test_schema_rejects_invalid_engine(tmp_path: Path) -> None:
    path = _write_yml(
        tmp_path / "bad_engine.yml",
        {
            "rule_id": "X",
            "engine": "parse",
            "cases": [{"bucket": "happy", "case_id": "01", "status": "needs-fixture"}],
        },
    )
    with pytest.raises(ValueError, match="invalid engine"):
        load_rule_cases(path)


def test_schema_rejects_invalid_bucket(tmp_path: Path) -> None:
    path = _write_json(
        tmp_path / "bad_bucket.json",
        {
            "rule_id": "X",
            "engine": "lint",
            "cases": [{"bucket": "meh", "case_id": "01", "status": "needs-fixture"}],
        },
    )
    with pytest.raises(ValueError, match="invalid bucket"):
        load_rule_cases(path)


def test_schema_rejects_invalid_status(tmp_path: Path) -> None:
    path = _write_yml(
        tmp_path / "bad_status.yml",
        {
            "rule_id": "X",
            "engine": "lint",
            "cases": [{"bucket": "happy", "case_id": "01", "status": "draft"}],
        },
    )
    with pytest.raises(ValueError, match="invalid status"):
        load_rule_cases(path)


def test_schema_ready_requires_tac(tmp_path: Path) -> None:
    path = _write_yml(
        tmp_path / "ready_no_tac.yml",
        {
            "rule_id": "X",
            "engine": "lint",
            "cases": [
                {
                    "bucket": "happy",
                    "case_id": "01",
                    "status": "ready",
                    "expect": {"accept": True},
                }
            ],
        },
    )
    with pytest.raises(ValueError, match=r"ready.*tac"):
        load_rule_cases(path)


def test_schema_needs_fixture_allows_null_tac(tmp_path: Path) -> None:
    path = _write_yml(
        tmp_path / "pending.yml",
        {
            "rule_id": "X",
            "engine": "lint",
            "cases": [
                {
                    "bucket": "edge_pass",
                    "case_id": "01",
                    "status": "needs-fixture",
                    "meta": {"reason": "fill later"},
                }
            ],
        },
    )
    cases = load_rule_cases(path)
    assert cases[0].tac is None
    assert cases[0].status == "needs-fixture"


def test_schema_oos_requires_cite(tmp_path: Path) -> None:
    path = _write_yml(
        tmp_path / "oos.yml",
        {
            "rule_id": "X",
            "engine": "lint",
            "cases": [{"bucket": "sad", "case_id": "01", "status": "oos"}],
        },
    )
    with pytest.raises(ValueError, match=r"oos.*cite"):
        load_rule_cases(path)


def test_schema_rejects_duplicate_node_ids(tmp_path: Path) -> None:
    path = _write_yml(
        tmp_path / "dup.yml",
        {
            "rule_id": "X",
            "engine": "lint",
            "cases": [
                {
                    "bucket": "happy",
                    "case_id": "01",
                    "status": "needs-fixture",
                    "meta": {"reason": "a"},
                },
                {
                    "bucket": "happy",
                    "case_id": "01",
                    "status": "needs-fixture",
                    "meta": {"reason": "b"},
                },
            ],
        },
    )
    with pytest.raises(ValueError, match="duplicate node_id"):
        load_rule_cases(path)


def test_discover_rule_case_files_under_testdata_layout(tmp_path: Path) -> None:
    root = tmp_path / "testdata"
    _write_yml(
        root / "lint" / "metar_speci" / "A.yml",
        {
            "rule_id": "A",
            "engine": "lint",
            "cases": [
                {
                    "bucket": "happy",
                    "case_id": "01",
                    "status": "needs-fixture",
                    "meta": {"reason": "a"},
                }
            ],
        },
    )
    _write_json(
        root / "convert" / "metar_speci" / "metar_nil.json",
        {
            "rule_id": "metar_nil",
            "engine": "convert",
            "cases": [
                {
                    "bucket": "sad",
                    "case_id": "01",
                    "status": "needs-fixture",
                    "meta": {"reason": "b"},
                }
            ],
        },
    )
    _write_yml(
        root / "validate" / "metar_speci" / "SCH.yml",
        {
            "rule_id": "METAR_SPECI.X-1",
            "engine": "validate",
            "cases": [
                {
                    "bucket": "edge_fail",
                    "case_id": "02",
                    "status": "oos",
                    "meta": {"cite": "S02.M2"},
                }
            ],
        },
    )
    # Noise files must be ignored.
    (root / "README.md").write_text("# ignore\n", encoding="utf-8")
    (root / "lint" / "metar_speci" / "notes.txt").write_text("x\n", encoding="utf-8")

    found = discover_rule_case_files(root)
    # Sorted by full path → convert / lint / validate
    assert [p.name for p in found] == ["metar_nil.json", "A.yml", "SCH.yml"]
    assert all(p.suffix.lower() in {".yml", ".yaml", ".json"} for p in found)


def test_load_rule_cases_tree_collects_all_engines(tmp_path: Path) -> None:
    root = tmp_path / "testdata"
    _write_yml(
        root / "lint" / "metar_speci" / "A.yml",
        {
            "rule_id": "A",
            "engine": "lint",
            "cases": [
                {
                    "bucket": "happy",
                    "case_id": "01",
                    "status": "needs-fixture",
                    "meta": {"reason": "a"},
                }
            ],
        },
    )
    _write_json(
        root / "convert" / "metar_speci" / "B.json",
        {
            "rule_id": "B",
            "engine": "convert",
            "cases": [
                {
                    "bucket": "sad",
                    "case_id": "01",
                    "status": "needs-fixture",
                    "meta": {"reason": "b"},
                }
            ],
        },
    )
    cases = load_rule_cases_tree(root)
    assert {c.engine for c in cases} == {"lint", "convert"}
    assert {c.node_id for c in cases} == {"A/happy/01", "B/sad/01"}
    assert all(isinstance(c, RuleCase) for c in cases)


def test_buckets_constant_matches_design() -> None:
    assert BUCKETS == ("happy", "sad", "edge_pass", "edge_fail")
