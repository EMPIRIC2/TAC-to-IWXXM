"""Profile-scoped IWXXM version lines (EV-064 / CA_ECCC)."""

from __future__ import annotations

import pytest

from src.config.iwxxm_versions import (
    VersionDeprecatedError,
    get_version_config,
    get_version_config_for_emit_profile,
)


def test_3_0_0_rejected_without_ca_profile() -> None:
    with pytest.raises(VersionDeprecatedError):
        get_version_config("3.0.0")


def test_3_0_0_allowed_for_ca_eccc_emit_profile() -> None:
    config = get_version_config_for_emit_profile("3.0.0", "ca_eccc")
    assert config["namespace_uri"] == "http://icao.int/iwxxm/3.0"


def test_3_0_0_still_rejected_for_annex3_emit_profile() -> None:
    with pytest.raises(VersionDeprecatedError):
        get_version_config_for_emit_profile("3.0.0", "annex3")
