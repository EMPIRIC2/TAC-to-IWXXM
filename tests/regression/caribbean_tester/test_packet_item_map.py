"""PACKET_ITEM_MAP completeness guard.

[Corpus: tests]
"""

from __future__ import annotations

import json
from pathlib import Path

_MAP = Path(__file__).resolve().parent / "fixtures" / "PACKET_ITEM_MAP.json"


def test_packet_item_map_nearly_complete() -> None:
    data = json.loads(_MAP.read_text(encoding="utf-8"))
    items = data["items"]
    assert data["total_items"] == len(items)
    assert data["pct_with_tests"] >= 97.0
    deferred_ok = {"Q19", "Q20", "N1a", "N1c", "N15"}
    missing = [
        item["packet_item_id"]
        for item in items
        if not item.get("test_node_ids") and item["packet_item_id"] not in deferred_ok
    ]
    assert missing == [], missing
    for item in items:
        if item["status"] == "COVERED":
            assert item.get("test_node_ids"), item["packet_item_id"]
