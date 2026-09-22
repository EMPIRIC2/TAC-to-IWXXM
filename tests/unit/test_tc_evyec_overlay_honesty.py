"""TC-EVYEC-001..005 — YAML/overlay honesty + preflight (#1224 / UJ-DEV-010)."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_MATRIX = _REPO / "docs" / "domain" / "overlays" / "product-engine-matrix.md"
_COOKBOOK = _REPO / "docs" / "domain" / "overlays" / "overlay-cookbook.md"
_PREFLIGHT = _REPO / "scripts" / "overlays" / "preflight.py"

_PRODUCTS = ("METAR", "SPECI", "TAF", "SIGMET", "AIRMET", "VAA", "TCA")
_CELL_VOCAB = frozenset({"full", "partial", "stub", "N/A"})

_PACKAGE_READMES: tuple[tuple[Path, str], ...] = (
    (_REPO / "packages" / "tac-decoding" / "README.md", "TAC_DECODING_PACK_DIR"),
    (_REPO / "packages" / "tac-validate" / "README.md", "TAC_VALIDATE_POLICY_DIR"),
    (_REPO / "packages" / "iwxxm-validate" / "README.md", "IWXXM_VALIDATE_POLICY_DIR"),
    (_REPO / "packages" / "tac2iwxxm" / "README.md", "TAC2IWXXM_PROFILE_DIR"),
)

_FORBIDDEN_BODY_KEYS = frozenset(
    {
        "policy_yaml",
        "pack_yaml",
        "overlay_yaml",
        "tac_policy_yaml",
        "iwxxm_policy_yaml",
        "validation_policy_yaml",
    }
)


def test_tc_evyec_001_product_engine_matrix_present() -> None:
    """TC-EVYEC-001: honesty matrix lists core products and allowed cell vocabulary."""
    assert _MATRIX.is_file(), f"missing {_MATRIX.relative_to(_REPO)}"
    text = _MATRIX.read_text(encoding="utf-8")
    for product in _PRODUCTS:
        assert f"| {product} |" in text, f"matrix missing product row {product}"
    # Every data cell after product name should use the vocabulary.
    for line in text.splitlines():
        if (
            not line.startswith("| ")
            or line.startswith("| Product")
            or line.startswith("|---")
        ):
            continue
        if not any(f"| {p} |" in line for p in _PRODUCTS):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        # product + 6 engine columns
        assert len(cells) >= 7, line
        for cell in cells[1:7]:
            # allow parenthetical notes e.g. partial (Python plugins)
            base = cell.split("(", 1)[0].strip()
            assert base in _CELL_VOCAB, f"bad cell {cell!r} in {line}"


def test_tc_evyec_002_package_readmes_document_overlays() -> None:
    """TC-EVYEC-002: each package README names overlay env + cookbook."""
    assert _COOKBOOK.is_file()
    for readme, env_name in _PACKAGE_READMES:
        assert readme.is_file(), readme
        body = readme.read_text(encoding="utf-8")
        assert env_name in body, f"{readme.name} missing {env_name}"
        assert "overlay-cookbook" in body or "Overlay cookbook" in body, readme.name


def test_tc_evyec_003_overlay_preflight_examples() -> None:
    """TC-EVYEC-003: preflight accepts valid examples and rejects bad extends."""
    assert _PREFLIGHT.is_file()
    proc = subprocess.run(
        [sys.executable, str(_PREFLIGHT), "--all-examples"],
        cwd=_REPO,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert "all example overlays OK" in proc.stdout
    assert "starters" in proc.stdout


def test_tc_evyec_004_openapi_no_policy_yaml_body_fields() -> None:
    """TC-EVYEC-004: OpenAPI request bodies do not accept pack/policy YAML blobs."""
    snapshot = _REPO / "apps" / "frontend" / "openapi" / "openapi.json"
    assert snapshot.is_file(), "missing OpenAPI snapshot; run make openapi-refresh"
    schema = json.loads(snapshot.read_text(encoding="utf-8"))
    blob = json.dumps(schema)
    for key in _FORBIDDEN_BODY_KEYS:
        assert key not in blob, f"OpenAPI must not expose body field {key}"
    for path, methods in schema.get("paths", {}).items():
        if not isinstance(methods, dict):
            continue
        for method, op in methods.items():
            if not isinstance(op, dict):
                continue
            rb = op.get("requestBody")
            if not isinstance(rb, dict):
                continue
            content = rb.get("content") or {}
            for media in content.values():
                if not isinstance(media, dict):
                    continue
                props = ((media.get("schema") or {}).get("properties")) or {}
                for name in props:
                    assert name not in _FORBIDDEN_BODY_KEYS, (
                        f"{method.upper()} {path} property {name}"
                    )


def test_tc_evyec_005_glossary_single_home_documented() -> None:
    """TC-EVYEC-005: cookbook states glossary SoT is tac-decoding."""
    text = _COOKBOOK.read_text(encoding="utf-8")
    assert re.search(r"tac-decoding", text, re.I)
    assert re.search(r"Glossary SoT|glossary SoT|SoT.*tac-decoding", text, re.I)
    assert "TAC_DECODING_GLOSSARY_PATH" in text
