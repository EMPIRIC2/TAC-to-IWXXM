"""#1434 — ``toHaveCount(0)`` must sit next to an opposite-state proof.

[Corpus: tests] [Corpus: product]

``make test-coverage-scripts`` collects this file in the scripts-coverage job,
which runs on every pull request. E2E Full stays limited to promote.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E2E = ROOT / "apps" / "e2e"
_SKIP = {"node_modules", "dist", "test-results", "playwright-report"}
_ABSENCE = re.compile(r"toHaveCount\(\s*0\s*\)")
_CHUNK = re.compile(
    r"(?m)^(?=[ \t]*(?:export[ \t]+)?(?:async[ \t]+)?function[ \t]"
    r"|[ \t]*test(?:\.\w+)?\()"
)
_PROOF = "Opposite state"


def unproved_absences(text: str) -> list[int]:
    """Line numbers where absence is asserted without a nearby opposite state."""
    starts = [match.start() for match in _CHUNK.finditer(text)]
    offenders: list[int] = []
    for match in _ABSENCE.finditer(text):
        start = 0
        for candidate in starts:
            if candidate <= match.start():
                start = candidate
            else:
                break
        prior = text[max(start, match.start() - 800) : match.start()]
        if _PROOF not in prior:
            offenders.append(text[: match.start()].count("\n") + 1)
    return offenders


def test_bare_absence_is_rejected() -> None:
    bare = "  test('bare', async ({ page }) => {\n    await expect(loc).toHaveCount(0);\n  });\n"
    assert unproved_absences(bare) == [2]
    proved = (
        "  test('proved', async ({ page }) => {\n"
        "    // Opposite state: the control is visible before dismiss.\n"
        "    await expect(loc).toHaveCount(0);\n"
        "  });\n"
    )
    assert unproved_absences(proved) == []
    earlier = (
        "  test('one', async () => {\n"
        "    // Opposite state: shown in this test only.\n"
        "    await expect(one).toHaveCount(0);\n"
        "  });\n"
        "  test('two', async () => {\n"
        "    await expect(two).toHaveCount(0);\n"
        "  });\n"
    )
    assert unproved_absences(earlier) == [6]


def test_e2e_absence_checks_name_the_opposite_state() -> None:
    offenders: list[str] = []
    for path in E2E.rglob("*.ts"):
        if any(part in _SKIP for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        offenders.extend(f"{relative}:{line}" for line in unproved_absences(text))
    assert not offenders, "toHaveCount(0) without an opposite state: " + ", ".join(
        offenders
    )
