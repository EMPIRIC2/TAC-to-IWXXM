"""BUG-2026-11-02 — API image must run Schematron for IWXXM 2025-2.

Staging ``/validate`` emitted ``SCHEMATRON_SKIPPED`` (``unsupported query language
xslt2``) because the API Docker image installed pure-Python ``iwxxm-validate`` without
the PyO3 native extension. Vendor 2025-2 Schematron uses ``queryBinding="xslt2"``,
which the lxml path cannot evaluate; native Schematron must be baked into the image
so operator/API validate matches live-eval (Schematron on).

[Corpus: product §F2] [Corpus: product §F13] [Corpus: deploy]
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
DOCKERFILE = ROOT / "apps" / "backend" / "docker" / "Dockerfile"
SCH_2025_2 = (
    ROOT / "vendor" / "schemas" / "iwxxm" / "2025-2" / "IWXXM" / "rule" / "iwxxm.sch"
)


def test_bug_2026_11_02_vendor_2025_2_schematron_uses_xslt2() -> None:
    """Guard: 2025-2 Schematron still requires xslt2 (lxml cannot run it)."""
    text = SCH_2025_2.read_text(encoding="utf-8", errors="replace")[:4000]
    assert 'queryBinding="xslt2"' in text or "queryBinding='xslt2'" in text


def test_bug_2026_11_02_api_dockerfile_builds_iwxxm_validate_native() -> None:
    """API Dockerfile must maturin-build iwxxm_validate._rust and assert it loads."""
    df = DOCKERFILE.read_text(encoding="utf-8")
    assert "maturin" in df, "API image must install/build via maturin"
    assert "rust/Cargo.toml" in df or "build-iwxxm-validate-native" in df
    assert "rust_available" in df, "fail closed if native extension missing after build"


def test_bug_2026_11_02_validate_iwxxm_2025_2_runs_schematron_when_rust_present() -> (
    None
):
    """Policy: with native extension, 2025-2 must not soft-skip Schematron."""
    from iwxxm_validate import rust_available, validate_iwxxm

    from tac2iwxxm import convert

    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    result = convert(
        "METAR KJFK 121251Z 18008KT 10SM FEW250 22/12 A3012=",
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok
    assert result.xml

    report = validate_iwxxm(
        result.xml,
        iwxxm_version="2025-2",
        profile="annex3",
        levels=("schematron",),
    )
    skipped = [i for i in report.issues if i.code == "SCHEMATRON_SKIPPED"]
    assert skipped == [], f"native path must evaluate 2025-2 Schematron, got {skipped}"
