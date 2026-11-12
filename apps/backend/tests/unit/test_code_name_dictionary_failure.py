"""GET /code-name-dictionary load failures return a plain HTTP 500."""

from __future__ import annotations

import json
import re

import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

_PLANNING_IDS = re.compile(
    r"\[Corpus:|docs/sessions/|docs/feature-list|\bADR-\d+\b|\bEV-\d+\b|"
    r"(?<!\w)#\d{3,}\b|\bTC-[A-Z0-9-]+\b|\bUJ-\d+\b|\bS0\d+\b|\bE\d{2}-\d+\b|\bF\d+\b",
    re.IGNORECASE,
)

# Exception text must not be copied into the operator-visible error body.
_POISON = "ADR-022 EV-048 #951 TC-F7-002 [Corpus: api] docs/sessions/x docs/feature-list S011 UJ-016 E11-31 F21"

_LOAD_ERRORS = (OSError, TypeError, ValueError, RuntimeError)
_TARGETS = (
    "tac_decoding.filter_dictionary_entries",
    "tac_decoding.dictionary_facets",
)


def _raiser(exc_type: type[BaseException]):
    def _boom(*_args: object, **_kwargs: object) -> None:
        raise exc_type(_POISON)

    return _boom


@pytest.mark.parametrize("exc_type", _LOAD_ERRORS)
@pytest.mark.parametrize("target", _TARGETS)
def test_code_name_dictionary_load_error_returns_plain_500(
    monkeypatch: pytest.MonkeyPatch,
    exc_type: type[BaseException],
    target: str,
) -> None:
    """OSError, TypeError, ValueError, and RuntimeError map to a fixed 500 detail."""
    monkeypatch.setattr(target, _raiser(exc_type))
    response = client.get("/api/v1/code-name-dictionary")
    assert response.status_code == 500
    detail = response.json()["detail"]
    assert detail["code"] == "code_name_dictionary_unavailable"
    rendered = json.dumps(detail)
    assert _POISON not in rendered
    assert _PLANNING_IDS.search(rendered) is None
