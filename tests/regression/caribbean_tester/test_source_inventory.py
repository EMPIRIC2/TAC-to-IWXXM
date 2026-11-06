"""Every Downloads tester file is accounted for in the inventory.

[Corpus: tests]
"""

from __future__ import annotations

import json
from pathlib import Path

from .conftest import FIX, RAW

_JAMAICA_PNG_DIR = FIX / "images" / "jamaica"

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


def test_jamaica_png_fixtures_exist_tc_carib_009() -> None:
    """TC-CARIB-009: Jamaica PNG basenames from inventory exist under fixtures."""
    png_rows = [
        row
        for row in _INVENTORY["files"]
        if str(row["suffix"]).lower() == ".png"
        and str(row["path"]).startswith("JAMAICA IWXXM TESTING RESULTS/")
    ]
    assert len(png_rows) == 15
    for row in png_rows:
        basename = Path(str(row["path"])).name
        fixture_path = _JAMAICA_PNG_DIR / basename
        assert fixture_path.exists(), fixture_path
