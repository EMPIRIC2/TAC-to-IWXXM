"""TC-F6-038 — TAC template amendment catalog (EV-1274 / #1274).

Loads the sibling catalog and the playbook rule. Does not change emitters.
[Corpus: product §F6] [Corpus: product §F15] [Corpus: domain-profiles] [Corpus: tests]
"""

from __future__ import annotations

from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[3]
_CATALOG = _REPO / "docs" / "domain" / "profiles" / "template-amendments.yaml"
_PLAYBOOK = _REPO / "docs" / "domain" / "profiles" / "NATIONAL_PROFILE_PLAYBOOK.md"
_REQUIRED = {"id", "source", "product", "change", "inherits", "status", "tac_convertible"}
_STATUSES = {"done", "partial", "not_started"}
_NOT_CONVERTIBLE = {
    "amd82-metar-rvr-unbounded",
    "amd82-metar-temp-tenths",
    "amd82-qvaci-no-tac",
    "amd82-wafs-sigwx-no-tac",
}


def _load() -> dict[str, object]:
    data = yaml.safe_load(_CATALOG.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_tc_f6_038_schema() -> None:
    """Each amendment row has the locked fields and a legal status."""
    data = _load()
    rows = data.get("amendments")
    assert isinstance(rows, list)
    assert rows
    for row in rows:
        assert isinstance(row, dict)
        assert set(row) >= _REQUIRED
        assert row["status"] in _STATUSES
        assert isinstance(row["tac_convertible"], bool)
        assert isinstance(row["inherits"], list)


def test_tc_f6_038_amendment_82_products() -> None:
    """METAR/SPECI, VAA, and SWXA each have at least one Amendment 82 row."""
    rows = _load()["amendments"]
    assert isinstance(rows, list)
    products = {row["product"] for row in rows if isinstance(row, dict)}
    assert {"METAR/SPECI", "VAA", "SWXA"} <= products


def test_tc_f6_038_not_convertible() -> None:
    """IWXXM-only items are recorded and are not missing converter work."""
    rows = _load()["amendments"]
    assert isinstance(rows, list)
    by_id = {row["id"]: row for row in rows if isinstance(row, dict)}
    for row_id in _NOT_CONVERTIBLE:
        row = by_id[row_id]
        assert row["tac_convertible"] is False
        assert row["status"] == "done"


def test_tc_f6_038_playbook_rule() -> None:
    """The playbook treats a template update as a catalog row."""
    text = _PLAYBOOK.read_text(encoding="utf-8")
    assert "template-amendments.yaml" in text
    assert "country lint delta" in text
