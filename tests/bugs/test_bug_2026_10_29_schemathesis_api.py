"""BUG-2026-10-29 — Schemathesis must tolerate nested validate-multi generation.

CI Schemathesis on ``stage`` failed
``test_openapi_no_unexpected_server_error[POST /api/v1/validation/validate-multi]``
with Hypothesis ``FailedHealthCheck: filter_too_much`` (8 kept / 50 filtered).
The suite must suppress that health check for nested batch request bodies while
keeping ``max-examples`` ≤ 25.

[Corpus: product §F34] [Corpus: tests] [Corpus: api]
"""

from __future__ import annotations

from pathlib import Path

import schemathesis
from schemathesis.config import HealthCheck

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = (
    ROOT / "apps" / "backend" / "tests" / "contract" / "test_schemathesis_openapi.py"
)


def test_bug_2026_10_29_schemathesis_suppresses_filter_too_much() -> None:
    """Suite config must suppress Hypothesis filter_too_much (CI stage failure)."""
    source = CONTRACT.read_text(encoding="utf-8")
    assert "def _schemathesis_config" in source, (
        "expected _schemathesis_config() helper in "
        "apps/backend/tests/contract/test_schemathesis_openapi.py"
    )
    assert "suppress-health-check" in source
    assert "filter_too_much" in source

    # Mirror the suite helper contract: Config must accept and retain the suppress.
    config = schemathesis.Config.from_dict(
        {
            "generation": {"max-examples": 25},
            "suppress-health-check": ["filter_too_much"],
            "checks": {
                "not_a_server_error": {
                    "expected-statuses": ["2xx", "4xx", "501"],
                }
            },
        }
    )
    assert HealthCheck.filter_too_much in set(config.suppress_health_check)
    assert "SCHEMATHESIS_MAX_EXAMPLES" in source
    assert "_MAX_EXAMPLES > 25" in source
