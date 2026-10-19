"""CI regressions for the four open Playwright bugs.

The bugs job collects this module. Each detector fails on a broken snippet and
passes on the current tree. [Corpus: tests] TC-EV100-001..004.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E2E = ROOT / "apps" / "e2e"
LOGOUT_SPEC = E2E / "tc-ev060-1006-auth.e2e.spec.ts"
DECODE_SPEC = E2E / "tc-ev061-uj064-068.e2e.spec.ts"
PICKER_SPEC = E2E / "f6e-product-profile-pickers.e2e.spec.ts"
LOGOUT_CHECKER = ROOT / "scripts" / "ci" / "check_e2e_logout_fixture.py"
LOGOUT_FIXTURE = "apps/e2e/fixtures/ci-logout.json"
_SKIP_PARTS = {"node_modules", "dist", "test-results"}
_ABSENCE = re.compile(r"expect\((?P<loc>.{1,240}?)\)\.toHaveCount\(0\)", re.S)
_LOGOUT_MARKER = "logout returns to guest convert"
_DECODE_MARKER = "EV-061 T2 — UJ-064"


def _e2e_texts() -> dict[str, str]:
    texts: dict[str, str] = {}
    for path in E2E.rglob("*.ts"):
        if any(part in _SKIP_PARTS for part in path.parts):
            continue
        texts[str(path.relative_to(ROOT))] = path.read_text(encoding="utf-8")
    return texts


def unproved_absence_specs(files: dict[str, str]) -> list[str]:
    """Return specs whose toHaveCount(0) never shows the locator can match."""
    offenders: list[str] = []
    for name, text in files.items():
        for chunk in re.split(r"(?m)^(?=  test(?:\.\w+)?\()", text):
            compact = " ".join(chunk.split())
            for match in _ABSENCE.finditer(chunk):
                loc = " ".join(match.group("loc").split())
                proved = (
                    f"{loc}).toBeVisible" in compact
                    or f"{loc}).toHaveCount(1" in compact
                    or re.search(r"can match|opposite state", chunk, re.I)
                )
                if not proved:
                    offenders.append(name)
    return sorted(set(offenders))


def logout_block(spec: str) -> str:
    """Return the logout test body."""
    return spec.split(_LOGOUT_MARKER, 1)[1].split("\n  test(", 1)[0]


def decode_block(spec: str) -> str:
    """Return the UJ-064 describe body."""
    return spec.split(_DECODE_MARKER, 1)[1].split("test.describe(", 1)[0]


def picker_helper(spec: str) -> str:
    """Return the product-picker helper body."""
    return spec.split("function requireF6ePickers", 1)[1].split("\ntest.describe", 1)[0]


def test_absence_locators_on_stage_are_proved() -> None:
    offenders = unproved_absence_specs(_e2e_texts())
    assert not offenders, offenders


def test_unproved_absence_locator_is_reported() -> None:
    sample = (
        "  test('gone', async () => {\n"
        "    await expect(page.getByRole('button', { name: 'Save' })).toHaveCount(0);\n"
        "  });\n"
    )
    assert unproved_absence_specs({"apps/e2e/sample.e2e.spec.ts": sample}) == [
        "apps/e2e/sample.e2e.spec.ts"
    ]


def test_logout_block_on_stage_does_not_skip() -> None:
    block = logout_block(LOGOUT_SPEC.read_text(encoding="utf-8"))
    assert "test.skip" not in block


def test_logout_skip_is_reported() -> None:
    sample = (
        "test('TC: logout returns to guest convert', async () => {\n"
        "  test.skip(true, 'fixture missing');\n"
        "});\n"
    )
    assert "test.skip" in logout_block(sample)


def test_decode_rows_on_stage_are_required() -> None:
    block = decode_block(DECODE_SPEC.read_text(encoding="utf-8"))
    assert "if (await segments.count())" not in block
    assert "getByTestId('decode-segments')" in block
    assert "toBeVisible" in block
    assert "<?xml" in block
    assert "validate-iwxxm-report" in block


def test_decode_count_guard_is_reported() -> None:
    sample = (
        "test.describe('EV-061 T2 — UJ-064 Validate', () => {\n"
        "  if (await segments.count()) {\n"
        "    await expect(segments).toBeVisible();\n"
        "  }\n"
        "});\n"
        "test.describe('next', () => {\n"
    )
    block = decode_block(sample)
    assert "if (await segments.count())" in block


def test_picker_helper_on_stage_does_not_skip() -> None:
    helper = picker_helper(PICKER_SPEC.read_text(encoding="utf-8"))
    assert "test.skip" not in helper
    assert "toBeVisible" in helper


def test_picker_skip_is_reported() -> None:
    sample = (
        "async function requireF6ePickers() {\n"
        "  test.skip(true, 'picker absent');\n"
        "}\n"
        "test.describe('pickers', () => {\n"
    )
    assert "test.skip" in picker_helper(sample)


def _run_logout_checker(fixture: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["E2E_LOGOUT_FIXTURE"] = fixture
    return subprocess.run(
        [sys.executable, str(LOGOUT_CHECKER), str(ROOT)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_missing_logout_fixture_fails() -> None:
    missing = _run_logout_checker("apps/e2e/fixtures/missing-logout.json")
    assert missing.returncode == 1
    assert "missing" in missing.stderr

    unset = _run_logout_checker("  ")
    assert unset.returncode == 1
    assert "unset" in unset.stderr


def test_committed_logout_fixture_passes() -> None:
    present = _run_logout_checker(LOGOUT_FIXTURE)
    assert present.returncode == 0, present.stderr
    assert "example.invalid" not in present.stderr
