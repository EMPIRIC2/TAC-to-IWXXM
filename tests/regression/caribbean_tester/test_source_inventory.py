"""Every Downloads tester file is accounted for in the inventory.

[Corpus: tests]
"""

from __future__ import annotations

import json

from .conftest import FIX, RAW

_INVENTORY = json.loads(
    (FIX / "source_file_inventory.json").read_text(encoding="utf-8")
)


def test_inventory_covers_one_hundred_twenty_four_source_files() -> None:
    assert _INVENTORY["file_count"] == 124
    assert len(_INVENTORY["files"]) == 124


def test_every_inventory_row_has_an_ingest_status() -> None:
    allowed = {
        "raw_copy",
        "tac_extracted_to_jsonl",
        "zip_listed",
        "zip_text_extracted",
        "binary_evidence_skipped",
        "other_skipped",
    }
    for row in _INVENTORY["files"]:
        status = str(row["ingested"])
        assert status in allowed or status.startswith("zip_error:"), row


def test_raw_tree_has_tac_xml_and_xlsx() -> None:
    assert list(RAW.rglob("*.tac"))
    assert list(RAW.rglob("*.xml"))
    assert list(RAW.rglob("*.xlsx"))


def test_raw_copied_paths_exist_on_disk() -> None:
    for row in _INVENTORY["files"]:
        if row["ingested"] != "raw_copy":
            continue
        path = RAW / str(row["path"])
        assert path.is_file(), path
