"""Unit tests for iwxxm-us compatibility gate (#853 / TC-EV038-006)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.iwxxm.iwxxm_us_compat_gate import (
    LAG_POLICY_ID,
    build_gate_report,
    load_manifest_us_pin,
)

_REPO = Path(__file__).resolve().parents[2]
_ADOPT = _REPO / "docs" / "domain" / "iwxxm" / "RELEASE_LINE_ADOPTABILITY.md"


def test_load_manifest_us_pin_from_repo() -> None:
    pin = load_manifest_us_pin(_REPO / "vendor" / "manifest.json")
    assert pin["tag"] == "3.0"
    assert "iwxxm-us" in pin["local_path"]


def test_build_gate_report_includes_lag_policy(tmp_path: Path) -> None:
    manifest = {
        "bundles": {
            "iwxxm-us": {
                "tag": "3.0",
                "local_path": "vendor/schemas/iwxxm-us",
                "source_url": "https://example.test/iwxxm-us.tgz",
            }
        }
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    report = build_gate_report(
        default_version="2025-2",
        manifest_path=path,
    )
    assert "IWXXM default (SoT): 2025-2" in report
    assert "iwxxm-us pin: 3.0" in report
    assert LAG_POLICY_ID in report
    assert "Ship WMO-only first" in report


def test_adoptability_doc_links_gate_and_lag_policy() -> None:
    text = _ADOPT.read_text(encoding="utf-8")
    assert "#853" in text
    assert "iwxxm-us compatibility gate" in text
    assert "D-S046-853" in text
    assert "make iwxxm-us-compat-smoke" in text
    assert "TC-EV038-006" in text
