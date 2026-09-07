"""T4.6 cutover gate (C09c / TC-F6-020 cutover + UJ-001 local).

Fails until T4.7 wires ``/convert`` → tac2iwxxm and removes ``packages/gifts``.

Spec: docs/test-plan.md TC-F6-020 cutover gate, TC-001; docs/feature-list.md F6
cutover; D-S008-05-batch2 C09c.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_SRC = REPO_ROOT / "apps" / "backend" / "src"
GIFTS_PKG = REPO_ROOT / "packages" / "gifts"
ANNEX3_TEST = (
    REPO_ROOT
    / "packages"
    / "tac2iwxxm"
    / "tests"
    / "test_tc_f6_020_021_metar_speci_annex3.py"
)
US_TEST = (
    REPO_ROOT
    / "packages"
    / "tac2iwxxm"
    / "tests"
    / "test_tc_f6_003_metar_speci_iwxxm_us.py"
)
E2E_UJ001 = REPO_ROOT / "apps" / "e2e" / "tac-file-conversion.e2e.spec.ts"


def _python_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.py") if "__pycache__" not in p.parts]


def _imports_gifts(path: Path) -> list[str]:
    """Return import lines that reference the gifts package."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return []
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            hits.extend(
                alias.name
                for alias in node.names
                if alias.name == "gifts" or alias.name.startswith("gifts.")
            )
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod == "gifts" or mod.startswith("gifts."):
                hits.append(mod)
    return hits


def test_t46_annex3_and_us_golden_modules_present() -> None:
    assert ANNEX3_TEST.is_file(), "annex3 golden suite missing (T4.1)"
    assert US_TEST.is_file(), "iwxxm_us golden suite missing (T4.10)"


def test_t46_uj001_e2e_spec_present() -> None:
    """C09c: Playwright UJ-001 (TC-001) artifact must remain part of the cutover gate."""
    assert E2E_UJ001.is_file(), f"missing UJ-001 Playwright spec: {E2E_UJ001}"
    text = E2E_UJ001.read_text(encoding="utf-8")
    assert "convert" in text.lower() or "tac" in text.lower()


def test_t46_packages_gifts_removed() -> None:
    """Cutover deletes packages/gifts (ADR-014 / Q5=(ii))."""
    assert not GIFTS_PKG.exists(), (
        f"packages/gifts still present at {GIFTS_PKG}; T4.7 must delete it"
    )


def test_t46_no_gifts_imports_in_backend_src() -> None:
    """Backend must not import gifts after cutover."""
    offenders: list[str] = []
    for path in _python_files(BACKEND_SRC):
        hits = _imports_gifts(path)
        if hits:
            offenders.append(f"{path.relative_to(REPO_ROOT)}: {hits}")
    assert not offenders, "gifts imports remain in apps/backend/src:\n" + "\n".join(
        offenders
    )


def test_t46_local_tc001_convert_via_tac2iwxxm() -> None:
    """Local UJ-001/TC-001 equivalent: convert TAC → IWXXM without gifts."""
    from tac2iwxxm import convert

    tac = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="
    result = convert(tac, product="METAR", profile="annex3", iwxxm_version="2025-2")
    assert result.ok is True
    assert result.xml
    assert "<iwxxm:METAR" in result.xml
    # Must not require gifts at runtime for this path
    with pytest.raises(ImportError):
        __import__("gifts")
