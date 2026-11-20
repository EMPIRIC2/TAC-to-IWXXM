"""Shared helpers for live-check unit tests (no network).

[Corpus: product §F6] [Corpus: tests §TC-LIVE-FEEDS] [Corpus: api]
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from dissemination.allowlist import parse_allowlist

ALLOW = parse_allowlist("aviationweather.gov,api.met.no,api.dataplatform.knmi.nl,cdn.example.test")

TAC = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="
XML = '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>'


def ok_convert(*_a: Any, **_k: Any) -> SimpleNamespace:
    return SimpleNamespace(ok=True, xml=XML, issues=())


def fail_convert(*_a: Any, **_k: Any) -> SimpleNamespace:
    issue = SimpleNamespace(code="PARSE", message="bad group")
    return SimpleNamespace(ok=False, xml=None, issues=(issue,))


class FakeResponse:
    def __init__(
        self,
        text: str = "",
        *,
        status_code: int = 200,
        json_payload: object | None = None,
    ) -> None:
        self.text = text
        self.status_code = status_code
        self._json_payload = json_payload

    def json(self) -> object:
        if self._json_payload is None:
            raise ValueError("no json")
        return self._json_payload
