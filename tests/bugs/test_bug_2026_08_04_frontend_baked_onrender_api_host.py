"""BUG-2026-08-04 - FE must prefer /config.json API host; Docker must inject publishable key.

Production ``app.tac-to-iwxxm.com`` called suspended ``metar-to-iwxxm-api.onrender.com``
because ``apiBase.ts`` ignored runtime config, and the frontend Dockerfile never wrote
``supabase.publishableKey`` into ``config.json``.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
API_BASE = ROOT / "apps" / "frontend" / "src" / "utils" / "apiBase.ts"
DOCKERFILE = ROOT / "apps" / "frontend" / "Dockerfile"
CI_CD = ROOT / ".github" / "workflows" / "ci-cd.yml"
PROD_CONFIG = ROOT / "config" / "prod.json"


def test_bug_2026_08_04_api_base_uses_runtime_config() -> None:
    src = API_BASE.read_text(encoding="utf-8")
    assert (
        "runtime-config" in src or "getRuntimeConfig" in src or "getApiBaseUrl" in src
    )
    # Must not be Vite-only (the production failure mode).
    assert "import.meta.env.VITE_API_BASE_URL" not in src or "runtime-config" in src
    assert "from './runtime-config'" in src or 'from "./runtime-config"' in src


def test_bug_2026_08_04_dockerfile_injects_publishable_key() -> None:
    df = DOCKERFILE.read_text(encoding="utf-8")
    assert "VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY" in df
    assert "publishableKey" in df


def test_bug_2026_08_04_ci_and_prod_config_use_doks_hosts() -> None:
    ci = CI_CD.read_text(encoding="utf-8")
    assert "FRONTEND_VITE_API_BASE_URL: https://api.tac-to-iwxxm.com" in ci
    assert "FRONTEND_VITE_APP_URL: https://app.tac-to-iwxxm.com" in ci
    # Stale Render bake-args must not remain as the CI defaults.
    assert (
        "FRONTEND_VITE_API_BASE_URL: https://metar-to-iwxxm-api.onrender.com" not in ci
    )

    prod = PROD_CONFIG.read_text(encoding="utf-8")
    assert "https://api.tac-to-iwxxm.com" in prod
    assert "https://app.tac-to-iwxxm.com" in prod
