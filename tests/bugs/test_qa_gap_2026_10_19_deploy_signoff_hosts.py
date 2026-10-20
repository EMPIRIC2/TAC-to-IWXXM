"""Regression test: live signoff and rollback name the DOKS hosts.

Fails while ``docs/deploy.md`` still signs off against the Render API or
frontend host, or while the Rollback section tells the operator to redeploy
a Render deploy. Passes once those sentences are gone and Rollback names a
DOKS host. The staging hosts are ``api.staging.tac-to-iwxxm.com`` and
``app.staging.tac-to-iwxxm.com``. [Corpus: deploy] [Corpus: tests]
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOY = ROOT / "docs" / "deploy.md"
STAGING_HOSTS = (
    "https://api.staging.tac-to-iwxxm.com",
    "https://app.staging.tac-to-iwxxm.com",
)


def _section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    rest = text[start + len(heading) :]
    next_heading = rest.find("\n## ")
    if next_heading < 0:
        return rest
    return rest[:next_heading]


def test_live_signoff_and_rollback_name_doks_hosts() -> None:
    """Deploy runbook signoff and rollback use the DOKS hosts, not Render."""
    text = DEPLOY.read_text(encoding="utf-8")
    rollback = _section(text, "## Rollback")
    problems: list[str] = []
    if "metar-to-iwxxm-api.onrender.com" in text:
        problems.append("live signoff still uses the Render API host")
    if "metar-to-iwxxm-frontend-v4-web.onrender.com" in text:
        problems.append("live signoff still uses the Render frontend host")
    if "Redeploy previous Render deploy" in rollback:
        problems.append("rollback still says to redeploy a Render deploy")
    if not all(host in text for host in STAGING_HOSTS):
        problems.append("deploy doc does not name the staging DOKS hosts")
    if "tac-to-iwxxm.com" not in rollback and "DOKS" not in rollback:
        problems.append("rollback does not name a DOKS host")
    assert not problems, "live signoff still points at Render (G4): " + "; ".join(
        problems
    )
