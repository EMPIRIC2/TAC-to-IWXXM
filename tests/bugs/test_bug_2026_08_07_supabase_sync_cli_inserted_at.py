"""BUG-2026-08-07 — Supabase Sync must pin CLI; no Render frontend CORS leftovers.

CLI 2.112.0 ``supabase link`` fails decoding Management API ``api-keys[].inserted_at``
values that use a ``+00:00`` suffix (requires ``Z``). Pinning ``2.111.0`` is the
upstream workaround (supabase/cli#6115). Suspended Render frontend origins must not
remain in DOKS/prod CORS allow-lists.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "supabase-sync.yml"
DOKS_API_CM = ROOT / "deploy" / "doks" / "base" / "configmap-api.yaml"
DOKS_FE_CM = ROOT / "deploy" / "doks" / "base" / "configmap-frontend-runtime.yaml"
PROD_CONFIG = ROOT / "config" / "prod.json"
ENV_SYNC = ROOT / "docs" / "ops" / "env-sync-runbook.md"

RENDER_FRONTEND = "https://metar-to-iwxxm-frontend-v4-web.onrender.com"
PINNED_CLI = "2.111.0"


def _setup_cli_versions(workflow: str) -> list[str]:
    """Return every ``version:`` value under supabase/setup-cli steps."""
    # Split on uses lines so we only collect the matching ``with: version``.
    versions: list[str] = []
    lines = workflow.splitlines()
    for i, line in enumerate(lines):
        if "supabase/setup-cli@" not in line:
            continue
        # Scan following lines until next step-level key at same indent.
        for j in range(i + 1, min(i + 12, len(lines))):
            m = re.match(r"^\s+version:\s*(\S+)\s*$", lines[j])
            if m:
                versions.append(m.group(1).strip("'\""))
                break
            if re.match(r"^      - ", lines[j]):
                break
    return versions


def test_bug_2026_08_07_supabase_sync_pins_cli_not_latest() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    versions = _setup_cli_versions(text)
    assert versions, "expected supabase/setup-cli version pins in supabase-sync.yml"
    assert "latest" not in versions, (
        "supabase-sync.yml must not use version: latest "
        "(CLI 2.112.0 breaks link on api-keys inserted_at; see supabase/cli#6115)"
    )
    assert all(v == PINNED_CLI for v in versions), (
        f"expected all setup-cli pins to be {PINNED_CLI}, got {versions}"
    )


def test_bug_2026_08_07_no_render_frontend_cors_allowlist() -> None:
    for path in (DOKS_API_CM, DOKS_FE_CM, PROD_CONFIG):
        text = path.read_text(encoding="utf-8")
        assert RENDER_FRONTEND not in text, (
            f"{path.relative_to(ROOT)} must not allow-list suspended Render frontend"
        )


def test_bug_2026_08_07_env_sync_runbook_redirects_use_doks_host() -> None:
    text = ENV_SYNC.read_text(encoding="utf-8")
    assert "https://app.tac-to-iwxxm.com/**" in text
    assert f"{RENDER_FRONTEND}/**" not in text
