"""M3 / cutover — packages/gifts removed (ADR-014 / T4.7)."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACKAGES_GIFTS = ROOT / "packages" / "gifts"
TAC2IWXXM = ROOT / "packages" / "tac2iwxxm"


@pytest.mark.migration
class TestM3GiftsPackageRemoved:
    """After F6 cutover, gifts must be gone and tac2iwxxm present."""

    def test_packages_gifts_removed(self) -> None:
        assert not PACKAGES_GIFTS.exists(), (
            "packages/gifts must be deleted at cutover (T4.7)"
        )

    def test_tac2iwxxm_package_present(self) -> None:
        assert (TAC2IWXXM / "pyproject.toml").is_file()
        assert (TAC2IWXXM / "src" / "tac2iwxxm").is_dir()
