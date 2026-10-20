"""Regression test: staging smoke fails closed on connectivity.

Fails while ``ci-cd.yml`` forces ``STAGING_SMOKE_PYTEST`` off, or while a
non-200/204 CORS preflight in ``scripts/deploy/staging_smoke.sh`` does not
exit. Passes once the job leaves pytest enabled and a bad preflight fails
the script. [Corpus: tests] [Corpus: deploy]
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "ci-cd.yml"
SMOKE = ROOT / "scripts" / "deploy" / "staging_smoke.sh"


def _preflight_failure_exits(smoke: str) -> bool:
    needle = 'if [[ "${preflight}" != "200"'
    start = smoke.find(needle)
    if start < 0:
        return False
    then_at = smoke.find("then", start)
    else_at = smoke.find("\nelse", then_at)
    if then_at < 0 or else_at < 0:
        return False
    body = smoke[then_at:else_at]
    return "exit 1" in body


def test_staging_smoke_fails_closed_on_connectivity() -> None:
    """Staging CD enables connectivity pytest and fails on a bad CORS preflight."""
    workflow = WORKFLOW.read_text(encoding="utf-8")
    smoke = SMOKE.read_text(encoding="utf-8")
    problems: list[str] = []
    if 'STAGING_SMOKE_PYTEST: "0"' in workflow:
        problems.append(
            "ci-cd.yml sets STAGING_SMOKE_PYTEST to 0, so staging pytest is skipped"
        )
    if not _preflight_failure_exits(smoke):
        problems.append(
            "a CORS preflight other than 200 or 204 does not exit 1 in staging_smoke.sh"
        )
    assert not problems, "staging smoke is not fail-closed (G3): " + "; ".join(problems)
