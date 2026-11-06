"""TC-EV1308-002 (HTTP) — conversion family returns profile issue_type + summaries.

[Corpus: api] [Corpus: tests] #1308
"""

from __future__ import annotations

from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

_BOILERPLATE = "Semantic conversion profile "


def test_rule_catalogs_conversion_has_profile_type_and_readable_summary() -> None:
    response = client.get("/api/v1/rule-catalogs", params={"family": "conversion"})
    assert response.status_code == 200
    items = response.json()["items"]
    assert items
    for row in items:
        assert row["issue_type"] == "profile"
        assert row["summary"]
        assert not str(row["summary"]).startswith(_BOILERPLATE)
        assert row["issue_type"] != "policy"
