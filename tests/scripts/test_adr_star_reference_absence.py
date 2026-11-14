"""Absence gate: tracked sources must not embed literal ADR-<digits> tokens.

Covers evolve-auto test-matrix dimensions for the ADR-star removal:

* Success — clean tracked tree passes
* Failure — injected ADR-<digits> fails the scan
* Validation — allow detector regexes that use ``ADR-\\d`` (no digits)
* Mutation — create/update/delete of scanned text changes pass/fail

[Corpus: tests] [Corpus: system-spec]
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]

# Literal digits only — detector patterns using ``ADR-\d`` are allowed.
_ADR_DIGITS = re.compile(r"ADR-\d+", re.IGNORECASE)
_CORPUS_ADR = re.compile(r"\[Corpus:\s*" + "adr", re.IGNORECASE)

_SKIP_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".gz",
    ".whl",
    ".so",
    ".dylib",
    ".wasm",
    ".bin",
    ".pyc",
    ".eap",
    ".lock",
}


def _tracked_text_files() -> list[Path]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=_REPO_ROOT)
    out: list[Path] = []
    for part in raw.split(b"\0"):
        if not part:
            continue
        path = _REPO_ROOT / Path(part.decode())
        if not path.is_file():
            continue
        if path.suffix.lower() in _SKIP_SUFFIXES:
            continue
        out.append(path)
    return out


def _scan_text(text: str) -> list[str]:
    hits: list[str] = []
    for match in _ADR_DIGITS.finditer(text):
        hits.append(match.group(0))
    for match in _CORPUS_ADR.finditer(text):
        hits.append(match.group(0))
    return hits


def scan_tracked_sources() -> list[str]:
    """Return ``path:token`` hits for forbidden ADR references."""
    found: list[str] = []
    for path in _tracked_text_files():
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        if b"\0" in raw[:2048]:
            continue
        text = raw.decode("utf-8", errors="ignore")
        for token in _scan_text(text):
            found.append(f"{path.relative_to(_REPO_ROOT)}:{token}")
    return found


def test_tracked_sources_have_no_adr_digit_tokens() -> None:
    """Success / validation pass: clean tree has no ADR-<digits> or corpus-adr cites."""
    hits = scan_tracked_sources()
    assert hits == [], "Forbidden ADR references remain:\n" + "\n".join(hits[:50])


def test_injected_adr_digits_fail_scan() -> None:
    """Failure: injecting ADR-<digits> into text is detected."""
    poison = "note " + "ADR" + "-" + "018" + " leftover"
    assert _scan_text(poison) == ["ADR" + "-" + "018"]


def test_injected_corpus_adr_cite_fails_scan() -> None:
    """Failure: injecting a corpus adr cite is detected."""
    poison = "see [Corpus: " + "ad" + "r/" + "AD" + "R-" + "030]"
    hits = _scan_text(poison)
    assert any("Corpus" in h or "adr" in h.lower() for h in hits)


def test_detector_regex_without_digits_is_allowed() -> None:
    """Validation pass: ban-pattern source using ADR-\\d does not trip the digit scan."""
    detector = r"pattern: /\bADR-\d+\b/g"
    assert _scan_text(detector) == []


def test_mutation_create_update_delete_scan_permutations() -> None:
    """Mutation x validation: create/update/delete of ADR tokens flip scan results."""
    base = "operator copy without planning ids"
    assert _scan_text(base) == []

    # Create + validation fail
    created = base + " " + "ADR" + "-" + "054"
    assert _scan_text(created) == ["ADR" + "-" + "054"]

    # Update + validation fail → pass when digits removed via rewrite
    updated = created.replace("ADR" + "-" + "054", "strict raise policy")
    assert _scan_text(updated) == []

    # Delete + allowed: removing the token clears the hit
    deleted = created.replace("ADR" + "-" + "054", "")
    assert _scan_text(deleted) == []


@pytest.mark.parametrize(
    ("text", "expect_hit"),
    [
        ("plain prose", False),
        ("ADR" + "-" + "001", True),
        (r"\bADR-\d+\b", False),
        ("[Corpus: " + "ad" + "r/x]", True),
        ("[Corpus: system-spec]", False),
    ],
)
def test_scan_validation_matrix(text: str, expect_hit: bool) -> None:
    """Permute validation success/failure for representative snippets."""
    hits = _scan_text(text)
    assert bool(hits) is expect_hit
