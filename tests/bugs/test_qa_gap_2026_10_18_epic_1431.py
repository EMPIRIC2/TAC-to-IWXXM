"""Regression tests for QA-gap epic #1431.

Each test encodes the done condition of one child issue. It fails while that
gap is open and passes once the gap is closed. [Corpus: tests]
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E2E = ROOT / "apps" / "e2e"
WORKFLOW = ROOT / ".github" / "workflows" / "ci-cd.yml"
MAKEFILE = ROOT / "Makefile"

_SKIP_PARTS = {"node_modules", "dist", "test-results"}


def _e2e_sources() -> list[Path]:
    sources: list[Path] = []
    for path in E2E.rglob("*.ts"):
        if any(part in _SKIP_PARTS for part in path.parts):
            continue
        sources.append(path)
    return sources


def _test_chunks(text: str) -> list[str]:
    return re.split(r"(?m)^(?=  test(?:\.\w+)?\()", text)


def test_qa_gap_1432_openapi_contract_check_covers_every_operation() -> None:
    """#1432: a local status and required-field check exists and is green."""
    checker = ROOT / "scripts" / "ci" / "check_openapi_contract.py"
    assert checker.is_file(), (
        "no local OpenAPI contract check (#1432): "
        "add scripts/ci/check_openapi_contract.py"
    )
    completed = subprocess.run(
        [sys.executable, str(checker)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, (completed.stdout + completed.stderr)[-1500:]


def test_qa_gap_1433_four_packages_publish_coverage_xml() -> None:
    """#1433: auth, tac2iwxxm, tac-validate, and workflows emit coverage.xml in CI."""
    makefile = MAKEFILE.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    missing: list[str] = []
    if "--cov-report=xml:packages/workflows/coverage.xml" not in makefile:
        missing.append("Makefile does not write packages/workflows/coverage.xml")
    for package in ("auth", "tac2iwxxm", "tac-validate", "workflows"):
        xml_path = f"packages/{package}/coverage.xml"
        if xml_path not in workflow:
            missing.append(f"ci-cd.yml does not upload {xml_path}")
    upload = re.search(
        r"contains\(fromJSON\('(?P<packages>\[[^\]]+\])'\), matrix\.package\)",
        workflow,
    )
    packages = upload.group("packages") if upload else ""
    if '"workflows"' not in packages:
        missing.append("coverage-xml upload omits workflows")
    assert not missing, "; ".join(missing)


def test_qa_gap_1434_absence_locators_prove_they_can_match() -> None:
    """#1434: toHaveCount(0) shares its test with a proof the locator can match."""
    offenders: list[str] = []
    absence = re.compile(r"expect\((?P<loc>.{1,240}?)\)\.toHaveCount\(0\)", re.S)
    for path in _e2e_sources():
        text = path.read_text(encoding="utf-8")
        for chunk in _test_chunks(text):
            compact = " ".join(chunk.split())
            for match in absence.finditer(chunk):
                loc = " ".join(match.group("loc").split())
                proved = (
                    f"{loc}).toBeVisible" in compact
                    or f"{loc}).toHaveCount(1" in compact
                    or re.search(r"can match|opposite state", chunk, re.I)
                )
                if proved:
                    continue
                offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, (
        f"{len(set(offenders))} specs use toHaveCount(0) without proving the locator "
        "can match (#1434): " + ", ".join(sorted(set(offenders))[:8])
    )


def test_qa_gap_1435_accessible_names_are_not_broad_substrings() -> None:
    """#1435: a partial accessible name has a comment naming the one control."""
    name_re = re.compile(r"name:\s*/")
    offenders: list[str] = []
    for path in _e2e_sources():
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if not name_re.search(line):
                continue
            window = "\n".join(lines[max(0, index - 2) : index + 1])
            if re.search(r"targets\b", window, re.I):
                continue
            offenders.append(f"{path.relative_to(ROOT)}:{index + 1}")
    assert not offenders, "broad accessible names (#1435): " + ", ".join(offenders[:12])


def test_qa_gap_1436_first_locators_name_the_intended_match() -> None:
    """#1436: .first() stays only when a comment says multiple matches are intended."""
    offenders: list[str] = []
    for path in _e2e_sources():
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if ".first()" not in line:
                continue
            window = "\n".join(lines[max(0, index - 4) : index + 1])
            if re.search(r"multiple matches|product behavior", window, re.I):
                continue
            offenders.append(f"{path.relative_to(ROOT)}:{index + 1}")
    assert not offenders, "ambiguous .first() locators (#1436): " + ", ".join(
        offenders[:12]
    )


def test_qa_gap_1437_logout_does_not_skip_when_credentials_are_unset() -> None:
    """#1437: the logout spec fails closed instead of skipping."""
    spec = (E2E / "tc-ev060-1006-auth.e2e.spec.ts").read_text(encoding="utf-8")
    marker = "logout returns to guest convert"
    assert marker in spec
    logout = spec.split(marker, 1)[1].split("\n  test(", 1)[0]
    assert "test.skip" not in logout, (
        "logout still skips when the fixture is missing (#1437)"
    )


def test_qa_gap_1438_validate_iwxxm_requires_decode_rows() -> None:
    """#1438: the validate-IWXXM spec always requires decode rows."""
    spec = (E2E / "tc-ev061-uj064-068.e2e.spec.ts").read_text(encoding="utf-8")
    marker = "EV-061 T2 — UJ-064"
    assert marker in spec
    block = spec.split(marker, 1)[1].split("test.describe(", 1)[0]
    assert "if (await segments.count())" not in block
    assert "getByTestId('decode-segments')" in block
    assert "toBeVisible" in block
    assert "<?xml" in block


def test_qa_gap_1439_product_picker_absence_fails_the_test() -> None:
    """#1439: a missing product picker fails the spec instead of skipping."""
    spec = (E2E / "f6e-product-profile-pickers.e2e.spec.ts").read_text(encoding="utf-8")
    assert "function requireF6ePickers" in spec
    helper = spec.split("function requireF6ePickers", 1)[1].split("\ntest.describe", 1)[
        0
    ]
    assert "test.skip" not in helper, "product-picker absence still skips (#1439)"
