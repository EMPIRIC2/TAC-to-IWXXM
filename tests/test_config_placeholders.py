"""Regression test: ensure no placeholder Supabase credentials are committed
to config files that get baked into CI builds or pushed to Render via blueprint
sync.  Prevents recurrence of the 'Service Preflight Failed: Supabase
connectivity check failed' deploy failure caused by hardcoded placeholder URLs.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Patterns that indicate an unconfigured / placeholder value
_PLACEHOLDER_PATTERNS = [
    re.compile(r"YOUR_PROJECT_REF\.supabase\.co"),
    re.compile(r"sb_publishable_[A-Za-z0-9_]{10,}"),  # placeholder publishable key
]

# Config files that are checked into source and affect builds or Render deploys
_CONFIG_FILES = [
    ".github/workflows/ci-cd.yml",
    "deploy/doks/base/secret-api.yaml",
]


def _scan_file(rel_path: str) -> list[str]:
    """Return a list of 'file:line: snippet' strings for any placeholder hit."""
    fpath = REPO_ROOT / rel_path
    if not fpath.exists():
        return []
    hits = []
    for lineno, line in enumerate(fpath.read_text().splitlines(), start=1):
        hits.extend(
            f"{rel_path}:{lineno}: {line.strip()}"
            for pattern in _PLACEHOLDER_PATTERNS
            if pattern.search(line)
        )
    return hits


def test_no_placeholder_supabase_url_in_ci_config():
    """ci-cd.yml must not contain a literal YOUR_PROJECT_REF Supabase URL;
    it should reference a secret instead."""
    hits = _scan_file(".github/workflows/ci-cd.yml")
    assert not hits, (
        "Placeholder Supabase credentials found in CI config - "
        "use ${{ secrets.FRONTEND_VITE_SUPABASE_URL }} instead:\n" + "\n".join(hits)
    )


def test_no_placeholder_supabase_url_in_render_yaml():
    """The live API secret manifest must not hard-code a placeholder Supabase URL."""
    assert not (REPO_ROOT / "render.yaml").exists()
    hits = _scan_file("deploy/doks/base/secret-api.yaml")
    assert not hits, (
        "Placeholder Supabase credentials found in the API secret manifest:\n"
        + "\n".join(hits)
    )
