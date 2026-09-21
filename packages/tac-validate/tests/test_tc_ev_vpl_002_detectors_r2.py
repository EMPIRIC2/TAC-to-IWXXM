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


def test_detector_error_matrix(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from tac_validate.detectors import (
        EmitSpec,
        PreprocessSpec,
        _emit_issue,
        _parse_emit,
        _prepare_window,
        _re_flags,
        _resolve_python,
    )

    with pytest.raises(DetectorError, match="flags entries"):
        _re_flags([1])
    assert _re_flags(["MULTILINE", "DOTALL"]) != 0
    assert _parse_emit(None, required=False) is None
    with pytest.raises(DetectorError, match="emit spec required"):
        _parse_emit(None, required=True)
    with pytest.raises(DetectorError, match="emit spec must be a mapping"):
        _parse_emit([], required=True)
    with pytest.raises(DetectorError, match=r"emit\.code"):
        _parse_emit({"code": ""}, required=True)
    with pytest.raises(DetectorError, match="message_template"):
        _parse_emit({"code": "INVALID_VISIBILITY"}, required=True)
    with pytest.raises(DetectorError, match="capture_group"):
        _parse_emit({"code": "INVALID_VISIBILITY", "message_template": "x", "capture_group": -1}, required=True)
    with pytest.raises(DetectorError, match="span must be"):
        _parse_emit({"code": "INVALID_VISIBILITY", "message_template": "x", "span": "nope"}, required=True)
    with pytest.raises(DetectorError, match="preprocess must be"):
        load_detector_pack(_write(tmp_path, "p.yaml", _min_pack(preprocess="bad")))

    cases = [
        ("rules: [notmap]\n", "rule must be a mapping"),
        (
            "rules: [{kind: finditer, pattern: a, on_match: {code: INVALID_VISIBILITY, message_template: x}}]\n",
            "rule.id",
        ),
        ("rules: [{id: r, kind: nope}]\n", "rule.kind"),
        (
            "rules: [{id: r, kind: finditer, pattern: a, skip_if_codes: 1, on_match: {code: INVALID_VISIBILITY, message_template: x}}]\n",
            "skip_if_codes",
        ),
        (
            "rules: [{id: r, kind: finditer, pattern: a, flags: x, on_match: {code: INVALID_VISIBILITY, message_template: x}}]\n",
            "flags must be",
        ),
        (
            "id: \nproducts: [METAR]\nrules: [{id: r, kind: python, python: python:tac_validate.detectors:example_python_hatch}]\n",
            "id is required",
        ),
        ("id: x\nproducts: [METAR]\nrules: []\n", "rules must be"),
    ]
    for index, (frag, match) in enumerate(cases):
        body = (
            "schema_version: 1\nid: x\nproducts: [METAR]\n" + frag
            if not frag.startswith("id:")
            else "schema_version: 1\n" + frag
        )
        if "id: x\nproducts" not in body and not frag.startswith("id:"):
            body = "schema_version: 1\nid: x\nproducts: [METAR]\n" + frag
        path = tmp_path / f"m{index}.yaml"
        path.write_text(body, encoding="utf-8")
        with pytest.raises(DetectorError, match=match):
            load_detector_pack(path)

    with pytest.raises(DetectorError, match="python:"):
        _resolve_python("notpython:x")
    with pytest.raises(DetectorError, match="module:attr"):
        _resolve_python("python:onlymodule")
    with pytest.raises(DetectorError, match="module:attr"):
        _resolve_python("python:mod:")
    with pytest.raises(DetectorError, match="module:attr"):
        _resolve_python("python::attr")
    with pytest.raises(DetectorError, match="not callable"):
        _resolve_python("python:tac_validate.detectors:ENV_DETECTOR_DIR")

    window, off = _prepare_window("ABC=", PreprocessSpec(strip_terminator=True, before="ZZ"))
    assert window == "ABC"
    assert off == 0
    window2, off2 = _prepare_window("ABC=RMK FOO", PreprocessSpec(strip_terminator=True, before="RMK"))
    assert "RMK" not in window2
    assert off2 == 0
    emit = EmitSpec(
        code="INVALID_VISIBILITY",
        location=None,
        message_template="{product} {capture!r}",
        capture_group=99,
        span="match",
    )
    import re as _re

    m = _re.search(r"(a)", "a")
    assert m is not None
    issue = _emit_issue(emit, product="METAR", body_start=0, body_end=1, window_offset=0, match=m)
    assert issue.code == "INVALID_VISIBILITY"

    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_DIR", str(tmp_path / "missing-dir-file"))
    (tmp_path / "missing-dir-file").write_text("x", encoding="utf-8")
    catalog = load_detector_catalog()
    assert "metar-speci-r2-visibility" in catalog

    # empty TAC body
    issues = run_r2_visibility_detectors("   ", "METAR")
    assert any(i.code == "MISSING_VISIBILITY" for i in issues)

    # require_search budget
    path = tmp_path / "req_budget.yaml"
    path.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: reqb",
                "stage: parse_gate",
                "products: [METAR]",
                "rules:",
                "  - id: r",
                "    kind: require_search",
                "    pattern: NOMATCH",
                "    on_fail:",
                "      code: MISSING_VISIBILITY",
                "      message_template: '{product} m'",
                "      span: body",
            ]
        ),
        encoding="utf-8",
    )
    pack = load_detector_pack(path)
    with pytest.raises(DetectorError, match="budget exceeded"):
        run_detector_pack(pack, "METAR X=", "METAR", budget=0)

    # yml overlay + hatch emitting a code for skip path
    overlay = tmp_path / "ov"
    overlay.mkdir()
    (overlay / "h.yml").write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: hatch2",
                "stage: cross_field",
                "products: [METAR]",
                "rules:",
                "  - id: p",
                "    kind: python",
                "    python: python:tac_validate.detectors:example_python_hatch_emit",
                "  - id: after",
                "    kind: require_search",
                "    skip_if_codes: [INVALID_VISIBILITY]",
                "    pattern: NEVER",
                "    on_fail:",
                "      code: MISSING_VISIBILITY",
                "      message_template: '{product} m'",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_DIR", str(overlay))
    catalog2 = load_detector_catalog()
    assert "hatch2" in catalog2
    out = run_detector_pack(catalog2["hatch2"], "METAR KJFK=", "METAR")
    assert any(i.code == "INVALID_VISIBILITY" for i in out)
    assert not any(i.code == "MISSING_VISIBILITY" for i in out)

    # Force missing-pattern / unsupported-kind defensive branches via object surgery
    from tac_validate.detectors import DetectorPack, DetectorRule, EmitSpec, PreprocessSpec

    bad_rule = DetectorRule(
        id="x",
        kind="finditer",
        preprocess=PreprocessSpec(),
        pattern=None,
        flags=0,
        skip_if_codes=(),
        on_match=None,
        on_fail=None,
        python_ref=None,
    )
    bad_pack = DetectorPack(id="bad", stage="token", products=frozenset({"METAR"}), rules=(bad_rule,))
    with pytest.raises(DetectorError, match="missing pattern"):
        run_detector_pack(bad_pack, "METAR X=", "METAR")
    weird = DetectorRule(
        id="y",
        kind="finditer",
        preprocess=PreprocessSpec(),
        pattern="a",
        flags=0,
        skip_if_codes=(),
        on_match=EmitSpec(code="INVALID_VISIBILITY", location=None, message_template="{product} x", span="body"),
        on_fail=None,
        python_ref=None,
    )
    # Bypass type checker: mutate kind to an invalid value for the else branch
    object.__setattr__(weird, "kind", "nope")  # type: ignore[arg-type]
    weird_pack = DetectorPack(id="w", stage="token", products=frozenset({"METAR"}), rules=(weird,))
    with pytest.raises(DetectorError, match="unsupported detector kind"):
        run_detector_pack(weird_pack, "METAR a=", "METAR")

    from tac_validate.detectors import run_theme_pack

    with pytest.raises(DetectorError, match="not found"):
        run_theme_pack("no-such-pack-zzzz", "METAR X=", "METAR")


def _write(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


def _min_pack(**kwargs: object) -> str:
    prep = kwargs.get("preprocess")
    prep_line = f"    preprocess: {prep}\n" if prep is not None else ""
    return (
        "schema_version: 1\nid: x\nproducts: [METAR]\nrules:\n"
        "  - id: r\n    kind: finditer\n"
        f"{prep_line}"
        "    pattern: a\n"
        "    on_match:\n      code: INVALID_VISIBILITY\n      message_template: x\n"
    )
