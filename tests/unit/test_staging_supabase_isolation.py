"""Issue #949 — DOKS staging Auth must use dedicated Supabase staging project.

Covers evolve-auto test-matrix dimensions for config validation (no live-cloud
mutation of secrets in CI). Live Auth smoke remains a human blocker until
staging Kubernetes / GitHub Environment secrets are rotated.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
PROFILES = ROOT / "config" / "deploy" / "profiles"
DOKS = ROOT / "config" / "deploy" / "doks"
CI_CD = ROOT / ".github" / "workflows" / "ci-cd.yml"

PROD_REF = "ktvxijislbtgqapllmuk"
STAGING_REF = "zvfhtcxjopwuesrozpvu"
PROD_URL = f"https://{PROD_REF}.supabase.co"
STAGING_URL = f"https://{STAGING_REF}.supabase.co"


def _load_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _frontend_config_url(overlay: str) -> str:
    path = DOKS / "overlays" / overlay / "patch-configmap-frontend.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    raw = doc["data"]["config.json"]
    cfg = json.loads(raw)
    return str(cfg["supabase"]["url"])


@pytest.mark.unit
class TestStagingSupabaseIsolationSuccess:
    """S / V+: staging surfaces accept and declare staging Auth URL."""

    def test_staging_profile_url_is_staging_project(self) -> None:
        cfg = _load_json(PROFILES / "staging.json")
        assert cfg["environment"] == "staging"
        supabase = cfg["supabase"]
        assert isinstance(supabase, dict)
        assert supabase.get("url") == STAGING_URL

    def test_staging_overlay_frontend_url_is_staging_project(self) -> None:
        assert _frontend_config_url("staging") == STAGING_URL

    def test_staging_profile_matches_staging_overlay(self) -> None:
        profile_url = _load_json(PROFILES / "staging.json")["supabase"]["url"]
        assert profile_url == _frontend_config_url("staging")

    def test_prod_profile_and_overlay_remain_production(self) -> None:
        cfg = _load_json(PROFILES / "prod.json")
        assert cfg["supabase"]["url"] == PROD_URL
        assert _frontend_config_url("prod") == PROD_URL


@pytest.mark.unit
class TestStagingSupabaseIsolationFailure:
    """F / V-: staging must reject production Auth URL; prod must not flip."""

    def test_staging_profile_rejects_production_url(self) -> None:
        cfg = _load_json(PROFILES / "staging.json")
        assert cfg["supabase"]["url"] != PROD_URL
        assert PROD_REF not in str(cfg["supabase"]["url"])

    def test_staging_overlay_rejects_production_url(self) -> None:
        url = _frontend_config_url("staging")
        assert url != PROD_URL
        assert PROD_REF not in url

    def test_prod_overlay_rejects_staging_url(self) -> None:
        url = _frontend_config_url("prod")
        assert url != STAGING_URL
        assert STAGING_REF not in url


@pytest.mark.unit
class TestStagingSupabaseIsolationValidation:
    """Validation modes: required keys present; secret stubs stay placeholders."""

    def test_api_secret_stub_keeps_placeholder_not_live_urls(self) -> None:
        doc = yaml.safe_load(
            (DOKS / "base" / "secret-api.yaml").read_text(encoding="utf-8")
        )
        data = doc["stringData"]
        assert data["SUPABASE_URL"] == "REPLACE_ME_SUPABASE_AUTH_URL"
        assert data["SUPABASE_PUBLISHABLE_KEY"] == "REPLACE_ME_SUPABASE_PUBLISHABLE_KEY"
        assert PROD_REF not in data["SUPABASE_URL"]
        assert STAGING_REF not in data["SUPABASE_URL"]

    def test_staging_profile_has_required_supabase_and_api_shape(self) -> None:
        cfg = _load_json(PROFILES / "staging.json")
        for key in ("environment", "api", "supabase"):
            assert key in cfg
        api = cfg["api"]
        assert isinstance(api, dict)
        assert api.get("baseUrl") == "https://api.staging.tac-to-iwxxm.com"
        assert api.get("frontendUrl") == "https://app.staging.tac-to-iwxxm.com"
        origins = api.get("corsOrigins")
        assert isinstance(origins, list)
        assert "https://app.staging.tac-to-iwxxm.com" in origins
        assert "http://143.244.202.13" in origins
        # Must not advertise prod LB as a staging CORS origin.
        assert "http://168.144.12.70" not in origins

    def test_staging_frontend_configmap_json_parses(self) -> None:
        path = DOKS / "overlays" / "staging" / "patch-configmap-frontend.yaml"
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        cfg = json.loads(doc["data"]["config.json"])
        assert cfg["environment"] == "staging"
        assert cfg["supabase"]["url"] == STAGING_URL
        assert "publishableKey" not in cfg["supabase"]

    def test_deploy_job_rebinds_environment_scoped_vite_auth_secrets(self) -> None:
        text = CI_CD.read_text(encoding="utf-8")
        # Job-level rebind under `environment:` so staging Environment secrets win.
        assert (
            "FRONTEND_VITE_SUPABASE_URL: ${{ secrets.FRONTEND_VITE_SUPABASE_URL }}"
            in text
        )
        assert (
            "FRONTEND_VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY: "
            "${{ secrets.FRONTEND_VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY }}"
        ) in text
        # staging Environment selection for stage branch deploys.
        assert re.search(
            r"environment:\s*\$\{\{\s*github\.ref == 'refs/heads/stage' && 'staging'",
            text,
        )


@pytest.mark.unit
class TestStagingSupabaseDocsContract:
    """Docs name both project refs without embedding secret values."""

    @pytest.mark.parametrize(
        "path",
        [
            ROOT / "docs" / "ops-contract.md",
            ROOT / "docs" / "env-variable.md",
            DOKS / "README.md",
        ],
    )
    def test_docs_name_staging_and_prod_refs(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8")
        assert STAGING_REF in text
        assert PROD_REF in text
        # Docs may mention key *names*; they must not embed live key material.
        assert "eyJ" not in text
        assert "sbp_" not in text
