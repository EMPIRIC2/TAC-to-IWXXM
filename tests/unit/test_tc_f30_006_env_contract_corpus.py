"""T7.3 / TC-F30-006 - CORPUS + env-contract Auth-only Supabase (doc/contract gate).

Spec: docs/test-plan.md TC-F30-006; F30 AC6; ADR-033; #830.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
class TestTcF30006EnvContractCorpus:
    """Product DB = DATABASE_URL; Supabase = Auth keys only."""

    def test_env_contract_declares_auth_only_supabase(self) -> None:
        text = (ROOT / "docs/env-contract.md").read_text(encoding="utf-8")
        assert "DATABASE_URL" in text
        assert "Auth-only Supabase" in text or "Auth URL + keys only" in text
        assert "not** product PostgREST" in text
        assert "DigitalOcean Postgres" in text

    def test_adr_033_accepted_and_references_cutover(self) -> None:
        adr = ROOT / "docs/adr/ADR-033-platform-independence-auth-do-doks.md"
        assert adr.is_file(), "ADR-033 missing"
        text = adr.read_text(encoding="utf-8")
        assert "Accepted" in text
        assert "DATABASE_URL" in text
        assert "Supabase = Auth only" in text or "Auth-only" in text
        assert "DOKS" in text

    def test_corpus_lists_env_contract(self) -> None:
        corpus = (ROOT / "docs/CORPUS.md").read_text(encoding="utf-8")
        assert "env-contract.md" in corpus

    def test_deploy_doks_readme_pins_database_url_and_adr_033(self) -> None:
        readme = (ROOT / "deploy/doks/README.md").read_text(encoding="utf-8")
        assert "DATABASE_URL" in readme
        assert "ADR-033" in readme
        assert "SUPABASE_URL" in readme  # Auth secrets only

    def test_feature_list_f30_exists(self) -> None:
        fl = (ROOT / "docs/feature-list.md").read_text(encoding="utf-8")
        assert "F30" in fl
        assert "F31" in fl
