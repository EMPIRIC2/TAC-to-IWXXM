"""Runtime configuration contract tests (ADR-010 / S003).

Replaces legacy VITE_AUTH_SERVICE_URL checks — config JSON + canonical Supabase
env names are the source of truth for local and deploy wiring.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
FRONTEND_DIR = ROOT / "apps" / "frontend"


def _load_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class TestRuntimeConfigProfiles:
    """Committed config/*.json profiles satisfy env-contract.md."""

    @pytest.mark.parametrize("profile", ["local", "e2e", "prod"])
    def test_profile_has_required_keys(self, profile: str) -> None:
        cfg = _load_json(CONFIG_DIR / f"{profile}.json")
        for key in ("environment", "api", "supabase"):
            assert key in cfg

        api = cfg["api"]
        assert isinstance(api, dict)
        assert api.get("baseUrl")
        assert api.get("frontendUrl")
        assert isinstance(api.get("corsOrigins"), list)

        supabase = cfg["supabase"]
        assert isinstance(supabase, dict)
        assert supabase.get("url")

    def test_local_profile_uses_merged_api_ports(self) -> None:
        cfg = _load_json(CONFIG_DIR / "local.json")
        api = cfg["api"]
        assert isinstance(api, dict)
        assert str(api.get("baseUrl")).endswith(":18001")
        assert str(api.get("frontendUrl")).endswith(":18000")

    def test_e2e_profile_omits_retired_disable_auth(self) -> None:
        cfg = _load_json(CONFIG_DIR / "e2e.json")
        api = cfg["api"]
        assert isinstance(api, dict)
        assert "disableAuth" not in api

    def test_prod_cors_includes_doks_fe_placeholder(self) -> None:
        """T4.5 / D-S038-04-b2 — DOKS FE placeholder allowed before DNS pin (T6.3)."""
        cfg = _load_json(CONFIG_DIR / "prod.json")
        api = cfg["api"]
        assert isinstance(api, dict)
        origins = api.get("corsOrigins")
        assert isinstance(origins, list)
        assert "https://app.doks.placeholder.metar-iwxxm.local" in origins
        # Primary remain Render until T6.3 retargets baseUrl / liveE2e.
        assert str(api.get("baseUrl")).endswith("onrender.com")
        assert "doks.placeholder" not in str(api.get("baseUrl"))


class TestFrontendEnvExamples:
    """Minimal frontend secrets — runtime config carries non-secrets."""

    def test_frontend_env_example_is_minimal(self) -> None:
        example = FRONTEND_DIR / ".env.example"
        assert example.is_file()
        content = example.read_text(encoding="utf-8")
        assert "VITE_AUTH_SERVICE_URL" not in content
        assert "VITE_BACKEND_URL" not in content

    def test_root_env_example_documents_canonical_supabase_keys(self) -> None:
        example = ROOT / ".env.example"
        assert example.is_file()
        content = example.read_text(encoding="utf-8")
        assert "SUPABASE_PUBLISHABLE_KEY=" in content
        assert "SUPABASE_SECRET_KEY=" in content


class TestPrepareConfigScript:
    """prepare-config.sh writes apps/frontend/public/config.json."""

    def test_prepare_config_injects_publishable_key(self, tmp_path: Path) -> None:
        dest_dir = tmp_path / "public"
        env = {
            **dict(__import__("os").environ),
            "METAR_CONFIG_ENV": "e2e",
            "SUPABASE_PUBLISHABLE_KEY": "sb_publishable_test_key",
            "DEST_DIR": str(dest_dir),
        }
        result = subprocess.run(
            ["bash", str(ROOT / "scripts/frontend/prepare-config.sh")],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr or result.stdout

        written = _load_json(dest_dir / "config.json")
        supabase = written.get("supabase")
        assert isinstance(supabase, dict)
        assert supabase.get("publishableKey") == "sb_publishable_test_key"
        assert supabase.get("url")

        api = written.get("api")
        assert isinstance(api, dict)
        assert api.get("baseUrl")
        assert "disableAuth" not in api

    def test_prepare_config_requires_api_base_url(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text(
            json.dumps(
                {
                    "environment": "test",
                    "api": {"frontendUrl": "http://localhost:18000", "corsOrigins": []},
                    "supabase": {"url": "https://demo.supabase.co"},
                }
            ),
            encoding="utf-8",
        )
        dest_dir = tmp_path / "public"
        env = {
            **dict(__import__("os").environ),
            "CONFIG_SRC": str(bad),
            "SUPABASE_PUBLISHABLE_KEY": "sb_publishable_test_key",
            "DEST_DIR": str(dest_dir),
        }
        result = subprocess.run(
            ["bash", str(ROOT / "scripts/frontend/prepare-config.sh")],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0
        assert "api.baseUrl" in (result.stderr + result.stdout)
