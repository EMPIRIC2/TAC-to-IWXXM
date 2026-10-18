"""#1435 — accessible-name lookups must be exact or full-name anchored.

[Corpus: tests] [Corpus: product]

``make test-coverage-scripts`` collects this file on every pull request.
``tc-ev060-uj059-063.e2e.spec.ts`` stays off this guard.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E2E = ROOT / "apps" / "e2e"
_SKIP = {"node_modules", "dist", "test-results", "playwright-report"}
_OFF_BOARD = "tc-ev060-uj059-063.e2e.spec.ts"
_CALL = re.compile(r"\.(getBy(?:Role|Label))\s*\(")
_REGEX = re.compile(r"/((?:\\.|[^/\n])*)/[a-z]*")


def _call_end(text: str, open_paren: int) -> int | None:
    depth = 0
    for index in range(open_paren, min(len(text), open_paren + 1200)):
        char = text[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index + 1
    return None


def broad_accessible_names(text: str) -> list[int]:
    """Line numbers of substring getByRole / getByLabel names."""
    hits: list[int] = []
    for match in _CALL.finditer(text):
        end = _call_end(text, match.end() - 1)
        if end is None:
            continue
        snippet = text[match.start() : end]
        partial = False
        for inner in _REGEX.findall(snippet):
            if not (inner.startswith("^") and inner.endswith("$")):
                partial = True
        exact = re.search(r"exact:\s*true", snippet) is not None
        string_name = re.search(r"name:\s*['\"]", snippet) is not None
        label_string = "getByLabel" in snippet and re.search(r"\(\s*['\"]", snippet)
        if partial or (not exact and (string_name or label_string)):
            hits.append(text[: match.start()].count("\n") + 1)
    return hits


def test_substring_accessible_names_are_rejected() -> None:
    broad = "page.getByRole('button', { name: /save/i })\n"
    assert broad_accessible_names(broad) == [1]
    exact = "page.getByRole('button', { name: 'Save', exact: true })\n"
    assert broad_accessible_names(exact) == []
    anchored = "page.getByLabel(/^TAC to IWXXM$/)\n"
    assert broad_accessible_names(anchored) == []
    label = "page.getByLabel(/Expand parameters/i)\n"
    assert broad_accessible_names(label) == [1]


def test_e2e_accessible_names_are_exact_or_anchored() -> None:
    offenders: list[str] = []
    for path in E2E.rglob("*.ts"):
        if path.name == _OFF_BOARD or any(part in _SKIP for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        offenders.extend(f"{relative}:{line}" for line in broad_accessible_names(text))
    assert not offenders, "broad accessible names: " + ", ".join(offenders)
