"""BUG/EV-033 - placeholder INGEST_POLLER_URL must fail closed (no silent loop).

Regression for DOKS cutover where metar-worker-secrets kept
``REPLACE_ME_INGEST_POLLER_URL`` and the worker could not ingest.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from metar_worker.poller import fetch_jobs
from metar_worker.poller_url import (
    DEFAULT_FIXTURE_INGEST_POLLER_URL,
    validate_ingest_poller_url,
)

ROOT = Path(__file__).resolve().parents[2]


def test_placeholder_secret_rejected() -> None:
    with pytest.raises(ValueError, match=r"placeholder|REPLACE_ME"):
        validate_ingest_poller_url("REPLACE_ME_INGEST_POLLER_URL")


def test_fetch_jobs_rejects_placeholder() -> None:
    with pytest.raises(ValueError, match="INGEST_POLLER_URL"):
        fetch_jobs("REPLACE_ME_INGEST_POLLER_URL")


def test_docs_pin_fixture_url() -> None:
    deploy = (ROOT / "docs/deploy.md").read_text(encoding="utf-8")
    env_contract = (ROOT / "docs/env-contract.md").read_text(encoding="utf-8")
    example = (ROOT / ".env.example").read_text(encoding="utf-8")
    for text in (deploy, env_contract, example):
        assert DEFAULT_FIXTURE_INGEST_POLLER_URL in text or (
            "raw.githubusercontent.com/EMPIRIC2/TAC-to-IWXXM/main/"
            "apps/worker/tests/fixtures/ingest_feed.json" in text
        )


def test_preflight_script_exists() -> None:
    script = ROOT / "scripts/deploy/doks_worker_poller_preflight.sh"
    assert script.is_file()
    body = script.read_text(encoding="utf-8")
    assert "REPLACE_ME" in body
    assert "scale" in body.lower()


def test_crashloop_check_script_exists() -> None:
    script = ROOT / "scripts/deploy/check_worker_crashloop.sh"
    assert script.is_file()
    body = script.read_text(encoding="utf-8")
    assert "CrashLoopBackOff" in body
