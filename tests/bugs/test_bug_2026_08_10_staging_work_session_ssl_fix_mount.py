"""BUG-2026-08-10 — do not ConfigMap-mount over work_session_service.py.

Staging returned ``NameError: UUID`` because a stale ``work-session-ssl-fix``
ConfigMap overrode the in-image module (which already includes ``_sync_database_url``
sslmode rewriting and ``from uuid import UUID, uuid4``).
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOY_API = ROOT / "deploy" / "doks" / "base" / "deployment-api.yaml"
SERVICE = ROOT / "apps" / "backend" / "src" / "services" / "work_session_service.py"


def test_bug_2026_08_10_deployment_does_not_mount_work_session_override() -> None:
    text = DEPLOY_API.read_text(encoding="utf-8")
    assert "work-session-ssl-fix" not in text
    assert "work_session_service.py" not in text or "Do not remount" in text


def test_bug_2026_08_10_work_session_service_imports_uuid_at_runtime() -> None:
    src = SERVICE.read_text(encoding="utf-8")
    assert "from uuid import UUID, uuid4" in src
    assert "UUID(self.user_id)" in src
    assert "uuid4()" in src
    assert "_sync_database_url" in src
