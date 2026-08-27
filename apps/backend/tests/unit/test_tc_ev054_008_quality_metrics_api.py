"""TC-EV054-008 - public quality-metrics HTTP API (+ TC-EV054-006 offline path)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.quality_metrics_store import clear_corpus_metrics_cache


@pytest.fixture
def client() -> TestClient:
    clear_corpus_metrics_cache()
    with TestClient(api_module.app) as c:
        yield c
    clear_corpus_metrics_cache()


def test_tc_ev054_008_list_and_filter(client: TestClient) -> None:
    r = client.get("/api/v1/quality-metrics")
    assert r.status_code == 200
    body = r.json()
    assert body["iwxxm_pin"] == "2025-2"
    assert len(body["files"]) == 18
    assert body["summaries"]

    metar = client.get("/api/v1/quality-metrics", params={"product": "metar"})
    assert metar.status_code == 200
    mbody = metar.json()
    assert all(f["product"] == "metar" for f in mbody["files"])
    assert all(s["product"] == "metar" for s in mbody["summaries"])


def test_tc_ev054_008_detail_and_unknown(client: TestClient) -> None:
    ok = client.get("/api/v1/quality-metrics/metar-A3-1")
    assert ok.status_code == 200
    detail = ok.json()
    assert detail["stem"] == "metar-A3-1"
    assert detail["match_status"] == "equal"
    assert detail["tac"]
    assert detail["official_xml"]
    assert detail["converted_xml"]
    assert "diff" not in detail

    missing = client.get("/api/v1/quality-metrics/not-a-real-stem")
    assert missing.status_code == 404
    assert "Unknown" in missing.json()["detail"]


def test_tc_ev054_006_missing_artifact_returns_503(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import src.quality_metrics_store as store

    clear_corpus_metrics_cache()
    monkeypatch.setattr(store, "_DEFAULT_ARTIFACT", tmp_path / "missing.json")
    clear_corpus_metrics_cache()
    r = client.get("/api/v1/quality-metrics")
    assert r.status_code == 503
    assert "unavailable" in r.json()["detail"].lower()
