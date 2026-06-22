"""Verify Makefile exposes live test harness targets (TC-LIVE-003)."""

from __future__ import annotations

from pathlib import Path

REQUIRED_TARGETS = (
    "test-live-connectivity",
    "test-live-api",
    "test-live-integration",
    "test-live-e2e",
    "test-live",
)


def test_makefile_declares_live_harness_targets() -> None:
    makefile = Path(__file__).resolve().parents[2] / "Makefile"
    content = makefile.read_text(encoding="utf-8")
    for target in REQUIRED_TARGETS:
        assert f"{target}:" in content, f"Makefile missing target: {target}"
