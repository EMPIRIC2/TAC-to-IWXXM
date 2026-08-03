"""T6.1 / #712 — DOKS kustomize base covers API + FE + worker + Auth/DB secrets."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

DOKS_BASE = Path("deploy/doks/base")
REQUIRED_RESOURCES = (
    "namespace.yaml",
    "configmap-api.yaml",
    "configmap-worker.yaml",
    "secret-api.yaml",
    "secret-worker.yaml",
    "deployment-api.yaml",
    "service-api.yaml",
    "ingress-api.yaml",
    "deployment-frontend.yaml",
    "service-frontend.yaml",
    "ingress-frontend.yaml",
    "deployment-worker.yaml",
    "kustomization.yaml",
)


@pytest.mark.unit
def test_doks_base_files_exist() -> None:
    assert DOKS_BASE.is_dir()
    for name in REQUIRED_RESOURCES:
        assert (DOKS_BASE / name).is_file(), name


@pytest.mark.unit
def test_kustomization_lists_all_workloads() -> None:
    doc = yaml.safe_load((DOKS_BASE / "kustomization.yaml").read_text(encoding="utf-8"))
    resources = set(doc["resources"])
    assert "deployment-api.yaml" in resources
    assert "deployment-frontend.yaml" in resources
    assert "deployment-worker.yaml" in resources
    assert doc["namespace"] == "metar-iwxxm"


@pytest.mark.unit
def test_api_secret_keys_include_database_and_auth() -> None:
    doc = yaml.safe_load((DOKS_BASE / "secret-api.yaml").read_text(encoding="utf-8"))
    keys = set(doc["stringData"])
    assert "DATABASE_URL" in keys
    assert "SUPABASE_URL" in keys
    assert "SUPABASE_JWKS_URL" in keys
    assert "SUPABASE_PUBLISHABLE_KEY" in keys


@pytest.mark.unit
def test_worker_secret_keys_include_database_and_poller() -> None:
    doc = yaml.safe_load((DOKS_BASE / "secret-worker.yaml").read_text(encoding="utf-8"))
    keys = set(doc["stringData"])
    assert "DATABASE_URL" in keys
    assert "INGEST_POLLER_URL" in keys


@pytest.mark.unit
def test_placeholder_ingress_hosts_match_deploy_spec() -> None:
    api = yaml.safe_load((DOKS_BASE / "ingress-api.yaml").read_text(encoding="utf-8"))
    fe = yaml.safe_load(
        (DOKS_BASE / "ingress-frontend.yaml").read_text(encoding="utf-8")
    )
    assert api["spec"]["rules"][0]["host"] == "api.doks.placeholder.metar-iwxxm.local"
    assert fe["spec"]["rules"][0]["host"] == "app.doks.placeholder.metar-iwxxm.local"


@pytest.mark.unit
def test_api_deployment_binds_port_and_health() -> None:
    doc = yaml.safe_load(
        (DOKS_BASE / "deployment-api.yaml").read_text(encoding="utf-8")
    )
    container = doc["spec"]["template"]["spec"]["containers"][0]
    assert container["ports"][0]["containerPort"] == 8000
    assert container["readinessProbe"]["httpGet"]["path"] == "/health"
    assert any(
        ref.get("secretRef", {}).get("name") == "metar-api-secrets"
        for ref in container["envFrom"]
    )


@pytest.mark.unit
def test_worker_has_no_service_or_ingress() -> None:
    """Worker is in-cluster only (no public HTTP)."""
    names = {p.name for p in DOKS_BASE.glob("*.yaml")}
    assert "service-worker.yaml" not in names
    assert "ingress-worker.yaml" not in names
