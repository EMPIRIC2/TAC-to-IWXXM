"""Shared loaders for EV-035 provenance tests."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MAP_JSON = REPO / "config" / "rules" / "PROVENANCE_MAP.json"
MAP_MD = REPO / "config" / "rules" / "PROVENANCE_MAP.md"
CATALOG_JSON = REPO / "config" / "rules" / "ISSUE_CATALOG.json"
MINING_DIR = REPO / "docs" / "domain" / "mining"  # local feeder (gitignored)
GAP_REPORT = REPO / "config" / "rules" / "provenance-gaps.md"

VALID_STATUSES = frozenset({"ok", "gap", "paywall", "N/A"})
VALID_ROLES = frozenset(
    {"validation", "conversion", "iwxxm-validation", "bulletin", "UI-decode"}
)
VALID_CONSUMERS = frozenset(
    {"tac-validate", "tac2iwxxm", "iwxxm-validate", "bulletin", "UI-decode"}
)
VALID_DISPOSITIONS = frozenset({"ok", "warn", "fail", "paywall", "N/A"})


def load_map() -> dict:
    assert MAP_JSON.is_file(), f"missing {MAP_JSON}"
    return json.loads(MAP_JSON.read_text(encoding="utf-8"))


def mining_note_files() -> list[Path]:
    return sorted(MINING_DIR.glob("*-mining-notes.md"))
