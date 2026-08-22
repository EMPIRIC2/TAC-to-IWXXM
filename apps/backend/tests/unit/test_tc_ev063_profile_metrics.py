"""TC-EV063-006 — profile id metrics + alias counters (EV-063 / F35).

Spec: docs/test-plan.md §TC-EV063-006; ADR-036 §6.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities import observability as observability_module
from src.utilities.profile_wire import WireProfileSelection
from src.utilities.security import verify_supabase_token

_SAMPLE_METAR = "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="


class _FakeCounter:
    def __init__(self) -> None:
        self.inc_calls = 0

    def inc(self) -> None:
        self.inc_calls += 1


class _FakeMetric:
    def __init__(self, child: _FakeCounter) -> None:
        self.child = child
        self.labels_calls: list[dict[str, str]] = []

    def labels(self, **kwargs: str) -> _FakeCounter:
        self.labels_calls.append(kwargs)
        return self.child


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _convert_files(**fields: tuple[None, str]) -> dict:
    base = {
        "manual_text": (None, _SAMPLE_METAR),
        "product": (None, "METAR"),
        "iwxxm_version": (None, "2025-2"),
        "lint": (None, "false"),
    }
    base.update(fields)
    return base


def _metric_sample(metrics_text: str, name: str, labels: dict[str, str]) -> float:
    """Return the counter sample for ``name`` with exact label set, or 0.0."""
    label_str = ",".join(f'{key}="{value}"' for key, value in sorted(labels.items()))
    prefix = f"{name}{{{label_str}}}"
    for line in metrics_text.splitlines():
        if line.startswith(prefix + " "):
            return float(line.split()[-1])
    return 0.0


def test_record_profile_wire_metrics_canonical_semantic(monkeypatch: pytest.MonkeyPatch) -> None:
    semantic_child = _FakeCounter()
    alias_child = _FakeCounter()
    exchange_child = _FakeCounter()
    semantic = _FakeMetric(semantic_child)
    alias = _FakeMetric(alias_child)
    exchange = _FakeMetric(exchange_child)

    monkeypatch.setattr(observability_module, "TAC_SEMANTIC_PROFILE_REQUESTS_TOTAL", semantic)
    monkeypatch.setattr(observability_module, "TAC_SEMANTIC_PROFILE_ALIAS_REQUESTS_TOTAL", alias)
    monkeypatch.setattr(observability_module, "TAC_EXCHANGE_PROFILE_REQUESTS_TOTAL", exchange)

    wire = WireProfileSelection(
        emit_key="annex3",
        semantic_canonical="icao_2025",
        deprecated_alias_used=False,
        exchange_profile=None,
    )
    observability_module.record_profile_wire_metrics("/api/v1/convert", wire)

    assert semantic_child.inc_calls == 1
    assert semantic.labels_calls == [{"route": "/api/v1/convert", "semantic_profile": "ICAO_2025"}]
    assert alias_child.inc_calls == 0
    assert exchange_child.inc_calls == 0


def test_record_profile_wire_metrics_alias_and_exchange(monkeypatch: pytest.MonkeyPatch) -> None:
    semantic_child = _FakeCounter()
    alias_child = _FakeCounter()
    exchange_child = _FakeCounter()
    semantic = _FakeMetric(semantic_child)
    alias = _FakeMetric(alias_child)
    exchange = _FakeMetric(exchange_child)

    monkeypatch.setattr(observability_module, "TAC_SEMANTIC_PROFILE_REQUESTS_TOTAL", semantic)
    monkeypatch.setattr(observability_module, "TAC_SEMANTIC_PROFILE_ALIAS_REQUESTS_TOTAL", alias)
    monkeypatch.setattr(observability_module, "TAC_EXCHANGE_PROFILE_REQUESTS_TOTAL", exchange)

    wire = WireProfileSelection(
        emit_key="annex3",
        semantic_canonical="icao_2025",
        deprecated_alias_used=True,
        exchange_profile="GLOBAL_AFS",
    )
    observability_module.record_profile_wire_metrics("/api/v1/convert-bulletin", wire)

    assert semantic_child.inc_calls == 1
    assert alias_child.inc_calls == 1
    assert exchange_child.inc_calls == 1
    assert alias.labels_calls == [{"route": "/api/v1/convert-bulletin", "semantic_profile": "ICAO_2025"}]
    assert exchange.labels_calls == [{"route": "/api/v1/convert-bulletin", "exchange_profile": "GLOBAL_AFS"}]


def test_tc_ev063_006_convert_increments_profile_metrics(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_convert(tac: str, **kwargs):
        return "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2025-2'/>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    before = client.get("/metrics").text
    response = client.post(
        "/api/v1/convert",
        files=_convert_files(
            semantic_profile=(None, "ICAO_2025"),
            exchange_profile=(None, "GLOBAL_AFS"),
        ),
    )
    assert response.status_code == 200, response.text[:400]
    after = client.get("/metrics").text

    semantic_before = _metric_sample(
        before,
        "tac_semantic_profile_requests_total",
        {"route": "/api/v1/convert", "semantic_profile": "ICAO_2025"},
    )
    semantic_after = _metric_sample(
        after,
        "tac_semantic_profile_requests_total",
        {"route": "/api/v1/convert", "semantic_profile": "ICAO_2025"},
    )
    assert semantic_after > semantic_before

    exchange_before = _metric_sample(
        before,
        "tac_exchange_profile_requests_total",
        {"route": "/api/v1/convert", "exchange_profile": "GLOBAL_AFS"},
    )
    exchange_after = _metric_sample(
        after,
        "tac_exchange_profile_requests_total",
        {"route": "/api/v1/convert", "exchange_profile": "GLOBAL_AFS"},
    )
    assert exchange_after > exchange_before


def test_tc_ev063_006_legacy_alias_increments_alias_counter(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_convert(tac: str, **kwargs):
        return "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2025-2'/>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    before = client.get("/metrics").text
    response = client.post(
        "/api/v1/convert",
        files=_convert_files(profile=(None, "annex3")),
    )
    assert response.status_code == 200, response.text[:400]
    after = client.get("/metrics").text

    alias_before = _metric_sample(
        before,
        "tac_semantic_profile_alias_requests_total",
        {"route": "/api/v1/convert", "semantic_profile": "ICAO_2025"},
    )
    alias_after = _metric_sample(
        after,
        "tac_semantic_profile_alias_requests_total",
        {"route": "/api/v1/convert", "semantic_profile": "ICAO_2025"},
    )
    assert alias_after > alias_before
