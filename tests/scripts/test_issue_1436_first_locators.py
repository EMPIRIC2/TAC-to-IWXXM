"""#1436 — ``.first()`` must not return under ``apps/e2e``.

[Corpus: tests] [Corpus: product]

``make test-coverage-scripts`` collects this file on every pull request.
E2E Full stays limited to promote.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E2E = ROOT / "apps" / "e2e"
_SKIP = {"node_modules", "dist", "test-results", "playwright-report"}
_FIRST = re.compile(r"\.first\s*\(")


def first_locators(text: str) -> list[int]:
    """Line numbers of ``.first()`` calls."""
    return [text[: match.start()].count("\n") + 1 for match in _FIRST.finditer(text)]


def test_first_call_is_rejected() -> None:
    assert first_locators("page.locator('card').first()\n") == [1]
    assert first_locators("page.getByTestId('card')\n") == []


def test_e2e_has_no_first_locators() -> None:
    offenders: list[str] = []
    for path in E2E.rglob("*.ts"):
        if any(part in _SKIP for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        offenders.extend(f"{relative}:{line}" for line in first_locators(text))
    assert not offenders, ".first() returned: " + ", ".join(offenders)
