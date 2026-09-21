"""TC-EV-VPL-001: TAC quality policy activate fail-closed (ADR-046 / #1216)."""

from __future__ import annotations

from pathlib import Path

import pytest
from tac_validate.policy import (
    PolicyActivationError,
    PolicyCycleError,
    PolicyDepthError,
    PolicyError,
    load_policy,
    load_policy_catalog,
    resolve_policy,
)


def test_load_activated_policy_with_known_codes(tmp_path: Path) -> None:
    path = tmp_path / "ok.yaml"
    path.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: test-ok",
                "lifecycle: activated",
                "product: metar",
                "select:",
                "  - INVALID_VISIBILITY",
                "  - MISSING_VISIBILITY",
                "ignore: []",
                "severity: {}",
                "preview: []",
            ]
        ),
        encoding="utf-8",
    )
    doc = load_policy(path)
    assert doc.id == "test-ok"
    assert doc.lifecycle == "activated"
    resolved = resolve_policy(doc, policies={doc.id: doc})
    assert resolved.can_activate is True
    assert resolved.warnings == ()
    assert "INVALID_VISIBILITY" in resolved.enabled_codes
    assert "MISSING_VISIBILITY" in resolved.enabled_codes


def test_draft_warns_on_unknown_code(tmp_path: Path) -> None:
    path = tmp_path / "draft.yaml"
    path.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: test-draft",
                "lifecycle: draft",
                "select:",
                "  - NOT_A_REAL_CODE_XYZ",
            ]
        ),
        encoding="utf-8",
    )
    doc = load_policy(path)
    resolved = resolve_policy(doc, policies={doc.id: doc})
    assert resolved.can_activate is False
    assert any("NOT_A_REAL_CODE_XYZ" in w for w in resolved.warnings)
    # draft does not raise
    assert resolved.lifecycle == "draft"


def test_activate_fails_closed_on_unknown_code(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: test-bad",
                "lifecycle: activated",
                "select:",
                "  - NOT_A_REAL_CODE_XYZ",
            ]
        ),
        encoding="utf-8",
    )
    doc = load_policy(path)
    with pytest.raises(PolicyActivationError, match="NOT_A_REAL_CODE_XYZ"):
        resolve_policy(doc, policies={doc.id: doc}, activate=True)


def test_extends_merges_and_later_wins(tmp_path: Path) -> None:
    base = tmp_path / "base.yaml"
    base.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: base",
                "lifecycle: activated",
                "select:",
                "  - INVALID_VISIBILITY",
                "ignore: []",
            ]
        ),
        encoding="utf-8",
    )
    child = tmp_path / "child.yaml"
    child.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: child",
                "lifecycle: activated",
                "extends:",
                "  - base",
                "ignore:",
                "  - INVALID_VISIBILITY",
                "select:",
                "  - MISSING_VISIBILITY",
            ]
        ),
        encoding="utf-8",
    )
    base_doc = load_policy(base)
    child_doc = load_policy(child)
    resolved = resolve_policy(
        child_doc,
        policies={"base": base_doc, "child": child_doc},
        activate=True,
    )
    assert "MISSING_VISIBILITY" in resolved.enabled_codes
    assert "INVALID_VISIBILITY" not in resolved.enabled_codes


def test_extends_cycle_detected(tmp_path: Path) -> None:
    a = tmp_path / "a.yaml"
    a.write_text(
        "schema_version: 1\nid: a\nlifecycle: draft\nextends: [b]\n",
        encoding="utf-8",
    )
    b = tmp_path / "b.yaml"
    b.write_text(
        "schema_version: 1\nid: b\nlifecycle: draft\nextends: [a]\n",
        encoding="utf-8",
    )
    a_doc = load_policy(a)
    b_doc = load_policy(b)
    with pytest.raises(PolicyCycleError):
        resolve_policy(a_doc, policies={"a": a_doc, "b": b_doc})


def test_extends_depth_capped(tmp_path: Path) -> None:
    policies = {}
    prev = None
    for i in range(7):
        pid = f"p{i}"
        path = tmp_path / f"{pid}.yaml"
        extends = f"extends: [{prev}]\n" if prev else "extends: []\n"
        path.write_text(
            f"schema_version: 1\nid: {pid}\nlifecycle: draft\n{extends}",
            encoding="utf-8",
        )
        policies[pid] = load_policy(path)
        prev = pid
    with pytest.raises(PolicyDepthError):
        resolve_policy(policies["p6"], policies=policies)


def test_empty_select_enables_non_preview_defaults(tmp_path: Path) -> None:
    path = tmp_path / "defaults.yaml"
    path.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: defaults",
                "lifecycle: activated",
                "product: metar",
                "select: []",
                "preview:",
                "  - AUTO_PRESENT",
            ]
        ),
        encoding="utf-8",
    )
    doc = load_policy(path)
    resolved = resolve_policy(doc, policies={doc.id: doc}, activate=True)
    assert "INVALID_VISIBILITY" in resolved.enabled_codes
    assert "AUTO_PRESENT" not in resolved.enabled_codes


def test_severity_unknown_code_fails_activate(tmp_path: Path) -> None:
    path = tmp_path / "sev.yaml"
    path.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: sev",
                "lifecycle: activated",
                "select:",
                "  - INVALID_VISIBILITY",
                "severity:",
                "  BOGUS_CODE: warning",
            ]
        ),
        encoding="utf-8",
    )
    doc = load_policy(path)
    with pytest.raises(PolicyActivationError, match="BOGUS_CODE"):
        resolve_policy(doc, policies={doc.id: doc}, activate=True)


def test_load_policies_from_dir_and_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    overlay = tmp_path / "overlay"
    overlay.mkdir()
    (overlay / "extra.yaml").write_text(
        "schema_version: 1\nid: extra\nlifecycle: draft\nselect: []\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("TAC_VALIDATE_POLICY_DIR", str(overlay))
    from tac_validate.policy import load_policy_catalog

    catalog = load_policy_catalog()
    assert "extra" in catalog
    assert "annex3-metar-quality" in catalog


def test_builtin_annex3_metar_policy_activates() -> None:
    from tac_validate.policy import load_policy_catalog

    catalog = load_policy_catalog()
    doc = catalog["annex3-metar-quality"]
    resolved = resolve_policy(doc, policies=catalog, activate=True)
    assert resolved.can_activate is True
    assert resolved.id == "annex3-metar-quality"


def test_parse_errors(tmp_path: Path) -> None:
    bad_root = tmp_path / "list.yaml"
    bad_root.write_text("- not a mapping\n", encoding="utf-8")
    with pytest.raises(PolicyError, match="mapping"):
        load_policy(bad_root)

    cases = [
        ("schema_version: 0\nid: x\n", "schema_version"),
        ("schema_version: 1\nid: ''\n", "id is required"),
        ("schema_version: 1\nid: x\nlifecycle: nope\n", "lifecycle"),
        ("schema_version: 1\nid: x\nproduct: 1\n", "product"),
        ("schema_version: 1\nid: x\nselect: notalist\n", "list of strings"),
        ("schema_version: 1\nid: x\nselect: [1]\n", "non-empty strings"),
        ("schema_version: 1\nid: x\nseverity: []\n", "severity must be a mapping"),
        ("schema_version: 1\nid: x\nseverity: {1: error}\n", "severity keys"),
        (
            "schema_version: 1\nid: x\nseverity: {INVALID_VISIBILITY: nope}\n",
            "must be one of",
        ),
        (
            "schema_version: 1\nid: x\nseverity: {INVALID_VISIBILITY: 3}\n",
            "must be one of",
        ),
    ]
    for index, (body, match) in enumerate(cases):
        path = tmp_path / f"case_{index}.yaml"
        path.write_text(body, encoding="utf-8")
        with pytest.raises(PolicyError, match=match):
            load_policy(path)


def test_unknown_extends_parent(tmp_path: Path) -> None:
    path = tmp_path / "orphan.yaml"
    path.write_text(
        "schema_version: 1\nid: orphan\nlifecycle: draft\nextends: [missing]\n",
        encoding="utf-8",
    )
    doc = load_policy(path)
    with pytest.raises(PolicyError, match="unknown extends parent"):
        resolve_policy(doc, policies={doc.id: doc})


def test_product_none_defaults_all_registry(tmp_path: Path) -> None:
    path = tmp_path / "all.yaml"
    path.write_text(
        "schema_version: 1\nid: all\nlifecycle: activated\nselect: []\n",
        encoding="utf-8",
    )
    doc = load_policy(path)
    resolved = resolve_policy(doc, policies={doc.id: doc}, activate=True)
    assert "UNKNOWN_PRODUCT" in resolved.enabled_codes


def test_detectors_and_severity_merge(tmp_path: Path) -> None:
    base = tmp_path / "base.yaml"
    base.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: base",
                "lifecycle: activated",
                "detectors: [d1]",
                "severity:",
                "  INVALID_VISIBILITY: warning",
            ]
        ),
        encoding="utf-8",
    )
    child = tmp_path / "child.yaml"
    child.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: child",
                "lifecycle: activated",
                "extends: [base]",
                "detectors: [d2]",
                "select: [INVALID_VISIBILITY]",
            ]
        ),
        encoding="utf-8",
    )
    base_doc = load_policy(base)
    child_doc = load_policy(child)
    resolved = resolve_policy(
        child_doc,
        policies={"base": base_doc, "child": child_doc},
        activate=True,
    )
    assert resolved.detector_ids == ("d2",)
    assert resolved.severity_overrides["INVALID_VISIBILITY"] == "warning"


def test_activate_flag_on_draft_unknown(tmp_path: Path) -> None:
    path = tmp_path / "draft.yaml"
    path.write_text(
        "schema_version: 1\nid: d\nlifecycle: draft\nselect: [NOPE]\n",
        encoding="utf-8",
    )
    doc = load_policy(path)
    with pytest.raises(PolicyActivationError, match="NOPE"):
        resolve_policy(doc, policies={doc.id: doc}, activate=True)


def test_overlay_yml_extension(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    overlay = tmp_path / "overlay"
    overlay.mkdir()
    (overlay / "extra.yml").write_text(
        "schema_version: 1\nid: yml-extra\nlifecycle: draft\nselect: []\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("TAC_VALIDATE_POLICY_DIR", str(overlay))
    from tac_validate.policy import load_policy_catalog

    catalog = load_policy_catalog()
    assert "yml-extra" in catalog


def test_overlay_env_ignored_when_not_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    file_path = tmp_path / "not-a-dir"
    file_path.write_text("x", encoding="utf-8")
    monkeypatch.setenv("TAC_VALIDATE_POLICY_DIR", str(file_path))
    from tac_validate.policy import load_policy_catalog

    catalog = load_policy_catalog()
    assert "annex3-metar-quality" in catalog
    assert "extra" not in catalog


def test_severity_empty_string_key(tmp_path: Path) -> None:
    path = tmp_path / "empty_key.yaml"
    path.write_text(
        "schema_version: 1\nid: ek\nseverity: {'': error}\n",
        encoding="utf-8",
    )
    with pytest.raises(PolicyError, match="severity keys"):
        load_policy(path)


def test_empty_product_string_treated_as_none(tmp_path: Path) -> None:
    path = tmp_path / "empty_prod.yaml"
    path.write_text(
        "schema_version: 1\nid: ep\nlifecycle: activated\nproduct: ''\nselect: [INVALID_VISIBILITY]\n",
        encoding="utf-8",
    )
    doc = load_policy(path)
    assert doc.product is None


def test_extension_header_layers_select_and_ignore(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    overlay = tmp_path / "overlay"
    overlay.mkdir()
    (overlay / "layer.yaml").write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: annex3-extra",
                "lifecycle: draft",
                "extends: [annex3-metar-quality]",
                "profiles: [annex3]",
                "select: [INVALID_VISIBILITY]",
                "ignore: [MISSING_VISIBILITY]",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("TAC_VALIDATE_POLICY_DIR", str(overlay))
    bare = load_policy_catalog()
    assert bare["annex3-metar-quality"].select == ()
    assert bare["annex3-metar-quality"].ignore == ()
    scoped = load_policy_catalog("annex3")
    assert scoped["annex3-metar-quality"].select == ("INVALID_VISIBILITY",)
    assert scoped["annex3-metar-quality"].ignore == ("MISSING_VISIBILITY",)
    other = load_policy_catalog("iwxxm_us")
    assert other["annex3-metar-quality"].select == ()

    (overlay / "layer.yaml").write_text(
        "schema_version: 1\nid: annex3-metar-quality\nlifecycle: draft\nselect: []\n",
        encoding="utf-8",
    )
    with pytest.raises(PolicyError, match="must extend one builtin"):
        load_policy_catalog("annex3")

    (overlay / "layer.yaml").write_text(
        "schema_version: 1\nid: brand-new\nprofiles: [annex3]\nselect: []\n",
        encoding="utf-8",
    )
    with pytest.raises(PolicyError, match="profiles require extends"):
        load_policy_catalog()

    (overlay / "layer.yaml").write_text(
        "schema_version: 1\nid: orphan\nextends: [missing]\nprofiles: [annex3]\nselect: []\n",
        encoding="utf-8",
    )
    with pytest.raises(PolicyError, match="unknown builtin"):
        load_policy_catalog("annex3")

    (overlay / "layer.yaml").write_text(
        "schema_version: 1\nid: wide\nextends: [annex3-metar-quality, annex3-metar-quality]\n"
        "profiles: [annex3]\nselect: []\n",
        encoding="utf-8",
    )
    with pytest.raises(PolicyError, match="must extend one builtin"):
        load_policy_catalog("annex3")

    (overlay / "layer.yaml").write_text(
        "schema_version: 1\nid: noprofiles\nextends: [annex3-metar-quality]\nselect: []\n",
        encoding="utf-8",
    )
    with pytest.raises(PolicyError, match="needs a profiles list"):
        load_policy_catalog("annex3")
