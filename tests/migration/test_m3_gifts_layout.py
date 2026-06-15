"""M3 layout checks — migration-plan.md Step 2, spec.md §packages/gifts."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACKAGES_GIFTS = ROOT / "packages" / "gifts"


@pytest.mark.migration
class TestM3GiftsPackageLayout:
    """packages/gifts contains the in-repo GIFTs source tree."""

    def test_packages_gifts_directory_exists(self) -> None:
        assert PACKAGES_GIFTS.is_dir(), "packages/gifts must exist after T3.2"

    def test_packages_gifts_has_encoder_module(self) -> None:
        encoder = PACKAGES_GIFTS / "gifts" / "metarEncoder.py"
        assert encoder.is_file(), "packages/gifts/gifts/metarEncoder.py required"

    def test_packages_gifts_has_pyproject(self) -> None:
        assert (PACKAGES_GIFTS / "pyproject.toml").is_file()

    def test_packages_gifts_has_tests_tree(self) -> None:
        assert (PACKAGES_GIFTS / "tests").is_dir()
