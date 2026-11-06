"""TC-CARIB-011: inventory DOCX must be harvest-linked or explicitly allowlisted.

[Corpus: tests]
"""

from __future__ import annotations

import json

from .conftest import FIX

_INVENTORY = json.loads(
    (FIX / "source_file_inventory.json").read_text(encoding="utf-8")
)
_ALLOWLIST = json.loads(
    (FIX / "docx_sourcing_allowlist.json").read_text(encoding="utf-8")
)
_MAP = json.loads((FIX / "PACKET_ITEM_MAP.json").read_text(encoding="utf-8"))
_DOCX_SOURCING_TEST = (
    "tests/regression/caribbean_tester/test_docx_sourcing.py"
    "::test_every_inventory_docx_is_harvest_linked_or_allowlisted"
)


def _harvest_docx_sources() -> set[str]:
    sources: set[str] = set()
    for path in FIX.glob("*.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            source = row.get("source")
            if source and str(source).lower().endswith(".docx"):
                sources.add(str(source))
    return sources


def _inventory_docx_paths() -> list[str]:
    return [
        str(row["path"])
        for row in _INVENTORY["files"]
        if str(row["suffix"]).lower() == ".docx"
    ]


def _map_docx_by_source_file() -> dict[str, dict[str, object]]:
    by_path: dict[str, dict[str, object]] = {}
    for item in _MAP["items"]:
        source_file = item.get("source_file")
        if isinstance(source_file, str) and source_file.lower().endswith(".docx"):
            by_path[source_file] = item
    return by_path


def test_every_inventory_docx_is_harvest_linked_or_allowlisted() -> None:
    harvest = _harvest_docx_sources()
    allowlisted = set(_ALLOWLIST["questionnaire_only"])
    assert len(allowlisted) == 13

    unclassified: list[str] = []
    for path in _inventory_docx_paths():
        if path in harvest or path in allowlisted:
            continue
        unclassified.append(path)

    assert unclassified == [], unclassified


def test_questionnaire_only_allowlist_matches_map_claims() -> None:
    by_path = _map_docx_by_source_file()
    harvest = _harvest_docx_sources()
    for path in _ALLOWLIST["questionnaire_only"]:
        assert path not in harvest, path
        item = by_path.get(path)
        assert item is not None, path
        notes = str(item.get("notes") or "")
        assert "docx_sourcing=questionnaire_only" in notes, item["packet_item_id"]
        assert _DOCX_SOURCING_TEST in item.get("test_node_ids", []), item[
            "packet_item_id"
        ]


def test_harvest_linked_docx_still_point_at_harvest_locks() -> None:
    harvest = _harvest_docx_sources()
    by_path = _map_docx_by_source_file()
    for path in sorted(harvest):
        item = by_path[path]
        locks = "tests/regression/caribbean_tester/test_harvest_extra_locks.py"
        assert locks in item.get("test_node_ids", []), item["packet_item_id"]
