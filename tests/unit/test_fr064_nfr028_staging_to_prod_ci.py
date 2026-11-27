"""FR-064 / NFR-028 — staging→prod CI wires live API + eval benchmark.

Offline contract tests (no live network). Mutation N/A for this read-only surface.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SMOKE = ROOT / "scripts" / "deploy" / "staging_smoke.sh"
WORKFLOW = ROOT / ".github" / "workflows" / "ci-cd.yml"
MAKEFILE = ROOT / "Makefile"


def test_staging_smoke_probes_eval_benchmark_success() -> None:
    """S / V+ — happy-path GET eval-benchmark with required body fields."""
    text = SMOKE.read_text(encoding="utf-8")
    assert "/api/v1/station-health/eval-benchmark" in text
    assert "computed_at" in text
    assert "product_breakdown" in text
    assert "exit 1" in text


def test_staging_smoke_probes_eval_benchmark_validation_reject() -> None:
    """V- / F - invalid ICAO filter must fail closed at 400."""
    text = SMOKE.read_text(encoding="utf-8")
    assert "icao=BAD" in text
    assert "expected 400" in text


def test_staging_smoke_keeps_fr045_live_map_eval() -> None:
    """Do not regress #1711 FR-045 probes while adding FR-064."""
    text = SMOKE.read_text(encoding="utf-8")
    assert "/api/v1/live-map/eval" in text
    assert "live-map/eval/refresh" in text


def test_ci_staging_smoke_runs_live_api_and_eval_benchmark() -> None:
    """NFR-028 — Staging smoke job runs curl smoke + make test-live-api."""
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "name: Staging smoke" in text
    assert "scripts/deploy/staging_smoke.sh" in text
    assert "make test-live-api" in text
    assert "FR-064" in text or "NFR-028" in text


def test_deploy_still_needs_test_job_for_wmo_golden_parity() -> None:
    """FR-064 — WMO/golden CI remains on the path that gates Deploy."""
    text = WORKFLOW.read_text(encoding="utf-8")
    # Deploy job declaration includes needs including test.
    deploy_idx = text.find("\n  deploy:\n")
    assert deploy_idx >= 0
    chunk = text[deploy_idx : deploy_idx + 800]
    assert "needs:" in chunk
    assert "test" in chunk


def test_makefile_exposes_test_live_api_target() -> None:
    """Read/query entrypoint used by Staging smoke remains defined."""
    text = MAKEFILE.read_text(encoding="utf-8")
    assert "test-live-api:" in text
    assert "test_live_api_health.py" in text
