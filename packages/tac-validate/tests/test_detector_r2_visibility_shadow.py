"""TC-EV-VPL-002/003/004 — detector DSL + R2 visibility shadow/flip (#1216 M2)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tac_validate import lint
from tac_validate.detectors import (
    DetectorError,
    compare_shadow,
    detector_mode,
    load_detector_catalog,
    load_detector_pack,
    run_detector_pack,
    run_r2_visibility_detectors,
)
from tac_validate.product_rules_pkg.metar_speci import _check_metar_speci

FIXTURES = Path(__file__).resolve().parent / "fixtures"
_MANIFEST = json.loads((FIXTURES / "manifest.json").read_text(encoding="utf-8"))
_R2_CODES = frozenset({"INVALID_VISIBILITY", "MISSING_VISIBILITY"})


def _read(rel: str) -> str:
    return (FIXTURES / rel).read_text(encoding="utf-8")


def _r2_cases() -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    cases.extend(c for c in _MANIFEST["accept"] if c.get("theme") == "R2")
    cases.extend(_MANIFEST.get("r2_fraction_accept", []))
    cases.extend(_MANIFEST.get("visibility_errors", []))
    cases.extend(
        c
        for c in _MANIFEST.get("negative", [])
        if "MISSING_VISIBILITY" in c.get("expected_codes", []) or "INVALID_VISIBILITY" in c.get("expected_codes", [])
    )
    return cases


def test_builtin_r2_pack_loads() -> None:
    catalog = load_detector_catalog()
    assert "metar-speci-r2-visibility" in catalog
    pack = catalog["metar-speci-r2-visibility"]
    assert pack.stage == "token"
    assert "METAR" in pack.products


@pytest.mark.parametrize("case", _r2_cases(), ids=lambda c: str(c["id"]))
def test_r2_shadow_code_span_parity(case: dict[str, object], monkeypatch: pytest.MonkeyPatch) -> None:
    tac = _read(str(case["tac"]))
    product = str(case["product"])
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "legacy")
    legacy = [i for i in _check_metar_speci(tac, product) if i.code in _R2_CODES]
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "detector")
    detector = run_r2_visibility_detectors(tac, product)
    cmp = compare_shadow(legacy, detector, codes=_R2_CODES)
    assert cmp.matched, f"legacy={sorted(cmp.legacy_keys)} detector={sorted(cmp.detector_keys)}"


def test_detector_mode_default_is_detector(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TAC_VALIDATE_DETECTOR_MODE", raising=False)
    assert detector_mode() == "detector"
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "nope")
    assert detector_mode() == "detector"
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "shadow")
    assert detector_mode() == "shadow"
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "legacy")
    assert detector_mode() == "legacy"


def test_r2_flip_lint_accept(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "detector")
    case = next(c for c in _MANIFEST["accept"] if c.get("theme") == "R2")
    report = lint(_read(str(case["tac"])), product=str(case["product"]))
    assert not any(i.code in _R2_CODES and i.severity == "error" for i in report.issues)


def test_python_hatch_rule(tmp_path: Path) -> None:
    path = tmp_path / "hatch.yaml"
    path.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: hatch-demo",
                "stage: token",
                "products: [METAR]",
                "rules:",
                "  - id: empty",
                "    kind: python",
                "    python: python:tac_validate.detectors:example_python_hatch",
            ]
        ),
        encoding="utf-8",
    )
    pack = load_detector_pack(path)
    issues = run_detector_pack(pack, "METAR KJFK 121255Z 10SM=", "METAR")
    assert issues == []


def test_token_scan_and_skip_if_match(tmp_path: Path) -> None:
    path = tmp_path / "scan.yaml"
    path.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: scan-demo",
                "stage: token",
                "products: [METAR]",
                "rules:",
                "  - id: bad_r",
                "    kind: token_scan",
                "    skip_if_match: '\\bNIL\\b'",
                "    select: '^R\\d{2}\\S*$'",
                "    ok: '^R\\d{2}/\\d{4}$'",
                "    on_fail:",
                "      code: INVALID_RVR",
                "      message_template: '{product} bad {capture!r}'",
                "      span: match",
                "  - id: skipped",
                "    kind: finditer",
                "    skip_if_match: '\\bNIL\\b'",
                "    pattern: '\\bNOSIG\\b'",
                "    on_match:",
                "      code: NOSIG_PRESENT",
                "      message_template: '{product} nosig'",
            ]
        ),
        encoding="utf-8",
    )
    pack = load_detector_pack(path)
    bad = run_detector_pack(pack, "METAR KJFK 121255Z R04/600=", "METAR")
    assert any(i.code == "INVALID_RVR" for i in bad)
    nil = run_detector_pack(pack, "METAR KJFK 121255Z NIL NOSIG=", "METAR")
    assert not any(i.code in {"INVALID_RVR", "NOSIG_PRESENT"} for i in nil)


def test_detector_parse_errors(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("- list\n", encoding="utf-8")
    with pytest.raises(DetectorError, match="mapping"):
        load_detector_pack(bad)

    cases = [
        ("id: x\nproducts: [METAR]\nrules: [{id: r, kind: finditer}]\n", "pattern"),
        ("id: x\nproducts: [METAR]\nrules: [{id: r, kind: python}]\n", "python"),
        ("id: x\nstage: nope\nproducts: [METAR]\nrules: [{id: r, kind: python, python: python:a:b}]\n", "stage"),
        ("id: x\nproducts: []\nrules: [{id: r, kind: python, python: python:a:b}]\n", "products"),
        (
            "id: x\nproducts: [METAR]\nrules: [{id: r, kind: finditer, pattern: a, flags: [NOPE], on_match: {code: INVALID_VISIBILITY, message_template: x}}]\n",
            "unsupported flag",
        ),
        (
            "id: x\nproducts: [METAR]\nrules: [{id: r, kind: token_scan, select: '^A$', ok: '^A$'}]\n",
            "on_ok and/or on_fail",
        ),
        (
            "id: x\nproducts: [METAR]\nrules: [{id: r, kind: token_scan, ok: '^A$', on_fail: {code: INVALID_VISIBILITY, message_template: x}}]\n",
            "select",
        ),
        (
            "id: x\nproducts: [METAR]\nrules: [{id: r, kind: finditer, pattern: a, max_emits: 0, on_match: {code: INVALID_VISIBILITY, message_template: x}}]\n",
            "max_emits",
        ),
    ]
    for index, (body, match) in enumerate(cases):
        path = tmp_path / f"err_{index}.yaml"
        path.write_text("schema_version: 1\n" + body, encoding="utf-8")
        with pytest.raises(DetectorError, match=match):
            load_detector_pack(path)


def test_budget_exceeded(tmp_path: Path) -> None:
    path = tmp_path / "budget.yaml"
    path.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: budget",
                "stage: token",
                "products: [METAR]",
                "rules:",
                "  - id: many",
                "    kind: finditer",
                "    pattern: '.'",
                "    on_match:",
                "      code: INVALID_VISIBILITY",
                "      message_template: '{product} x'",
            ]
        ),
        encoding="utf-8",
    )
    pack = load_detector_pack(path)
    with pytest.raises(DetectorError, match="budget exceeded"):
        run_detector_pack(pack, "METAR KJFK 121255Z ABCDEFGHIJ=", "METAR", budget=3)


def test_token_scan_budget_and_finditer_max_emits(tmp_path: Path) -> None:
    scan = tmp_path / "scan_budget.yaml"
    scan.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: scan-budget",
                "stage: token",
                "products: [METAR]",
                "rules:",
                "  - id: toks",
                "    kind: token_scan",
                "    select: '^.+$'",
                "    ok: '^NOPE$'",
                "    on_fail:",
                "      code: INVALID_RVR",
                "      message_template: '{product} x'",
            ]
        ),
        encoding="utf-8",
    )
    with pytest.raises(DetectorError, match="budget"):
        run_detector_pack(load_detector_pack(scan), "METAR A B C D=", "METAR", budget=2)

    limited = tmp_path / "max_find.yaml"
    limited.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: max-find",
                "stage: token",
                "products: [METAR]",
                "rules:",
                "  - id: a",
                "    kind: finditer",
                "    pattern: 'A'",
                "    max_emits: 1",
                "    on_match:",
                "      code: AUTO_PRESENT",
                "      message_template: '{product} a'",
            ]
        ),
        encoding="utf-8",
    )
    out = run_detector_pack(load_detector_pack(limited), "METAR AA=", "METAR")
    assert len([i for i in out if i.code == "AUTO_PRESENT"]) == 1


def test_preprocess_after_window(tmp_path: Path) -> None:
    path = tmp_path / "after.yaml"
    path.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: after-demo",
                "stage: token",
                "products: [METAR]",
                "rules:",
                "  - id: in_rmk",
                "    kind: finditer",
                "    preprocess:",
                "      after: RMK",
                "      exclude_ahl_lines: true",
                "    pattern: '\\bSLP\\d+\\b'",
                "    on_match:",
                "      code: INVALID_REMARK",
                "      message_template: '{product} {capture!r}'",
            ]
        ),
        encoding="utf-8",
    )
    issues = run_detector_pack(load_detector_pack(path), "METAR KJFK 121255Z 10SM RMK SLP17=", "METAR")
    assert any(i.code == "INVALID_REMARK" and "SLP17" in i.message for i in issues)
    # Marker absent → whole body searched; still finds SLP when present without RMK? none.
    none = run_detector_pack(load_detector_pack(path), "METAR KJFK 121255Z 10SM=", "METAR")
    assert none == []


def test_overlay_detector_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    overlay = tmp_path / "d"
    overlay.mkdir()
    (overlay / "extra.yaml").write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: extra-det",
                "stage: token",
                "products: [METAR]",
                "rules:",
                "  - id: noop",
                "    kind: require_search",
                "    pattern: METAR",
                "    on_fail:",
                "      code: MISSING_VISIBILITY",
                "      message_template: '{product} missing'",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_DIR", str(overlay))
    catalog = load_detector_catalog()
    assert "extra-det" in catalog


def test_skip_if_codes_skips_missing_when_invalid() -> None:
    tac = "METAR KJFK 121255Z 10000KM="
    issues = run_r2_visibility_detectors(tac, "METAR")
    codes = {i.code for i in issues}
    assert "INVALID_VISIBILITY" in codes
    assert "MISSING_VISIBILITY" not in codes


def test_wrong_product_returns_empty() -> None:
    catalog = load_detector_catalog()
    pack = catalog["metar-speci-r2-visibility"]
    assert run_detector_pack(pack, "TAF KJFK 1212/1312 10SM=", "TAF") == []
