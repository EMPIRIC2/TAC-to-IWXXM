"""TC-EV051-004 — deploy tag glob must match dotted ``vYYYY.MM.DD-deploy`` tags.

GitHub Actions ``on.push.tags`` uses ``*`` as "any chars except ``/``". The prior
pattern ``v*-*-deploy`` required **two** hyphens and therefore skipped
``v2026.09.04-deploy`` (one hyphen before ``deploy``), so prod Deploy never
started on tag push (2026-09-04 cutover used ``workflow_dispatch`` instead).

[Corpus: tests] [Corpus: deploy] [Corpus: product §F30]
"""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CI_CD = ROOT / ".github" / "workflows" / "ci-cd.yml"

# Canonical release tag shape from docs/deploy.md §Promote.
DOTTED_DEPLOY_TAG = "v2026.09.04-deploy"
HYPHENATED_DEPLOY_TAG = "v2026-09-04-deploy"


def _push_tag_patterns() -> list[str]:
    text = CI_CD.read_text(encoding="utf-8")
    # Narrow to the ``on.push.tags`` block (avoid matching later ``tags: |`` Docker meta).
    match = re.search(
        r"on:\s*\n(?:.*\n)*?\s+tags:\s*\n((?:\s+-\s+'[^']+'\s*\n)+)",
        text,
    )
    assert match is not None, "expected on.push.tags list in ci-cd.yml"
    return re.findall(r"-\s+'([^']+)'", match.group(1))


def test_ci_cd_push_tags_include_v_star_deploy() -> None:
    patterns = _push_tag_patterns()
    assert "v*-deploy" in patterns
    assert "v*-*-deploy" not in patterns


def test_dotted_deploy_tag_matches_workflow_glob() -> None:
    patterns = _push_tag_patterns()
    assert any(fnmatch.fnmatch(DOTTED_DEPLOY_TAG, p) for p in patterns), (
        f"{DOTTED_DEPLOY_TAG!r} must match on.push.tags {patterns}"
    )


def test_legacy_two_hyphen_glob_misses_dotted_tag() -> None:
    """Document why ``v*-*-deploy`` was wrong for the documented tag shape."""
    assert not fnmatch.fnmatch(DOTTED_DEPLOY_TAG, "v*-*-deploy")
    assert fnmatch.fnmatch(HYPHENATED_DEPLOY_TAG, "v*-*-deploy")


def test_hyphenated_deploy_tag_still_matches_v_star_deploy() -> None:
    assert fnmatch.fnmatch(HYPHENATED_DEPLOY_TAG, "v*-deploy")
