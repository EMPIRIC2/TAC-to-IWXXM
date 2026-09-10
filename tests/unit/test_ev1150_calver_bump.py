"""Unit tests for CalVer bump helper (EV-1150 / ADR-043)."""

from __future__ import annotations

from datetime import date

from scripts.pypi.bump_calver import calver_string, set_package_version


def test_calver_string_base_and_suffixes() -> None:
    assert calver_string(day=date(2026, 9, 10)) == "2026.9.10"
    assert calver_string(day=date(2026, 9, 10), same_day_n=2) == "2026.9.10.2"
    assert calver_string(day=date(2026, 9, 10), dev=7) == "2026.9.10.dev7"
    assert (
        calver_string(day=date(2026, 9, 10), same_day_n=1, dev=3) == "2026.9.10.1.dev3"
    )


def test_set_package_version_tac_validate() -> None:
    """Smoke that setter finds real package paths (integration-lite)."""
    from scripts.pypi import bump_calver as mod

    py = mod.PACKAGES["tac-validate"]["pyproject"]
    assert py.is_file()
    original = py.read_text(encoding="utf-8")
    init = mod.PACKAGES["tac-validate"]["init"]
    init_orig = init.read_text(encoding="utf-8")
    try:
        set_package_version("tac-validate", "2099.1.1")
        assert 'version = "2099.1.1"' in py.read_text(encoding="utf-8")
        assert '__version__ = "2099.1.1"' in init.read_text(encoding="utf-8")
    finally:
        py.write_text(original, encoding="utf-8")
        init.write_text(init_orig, encoding="utf-8")
