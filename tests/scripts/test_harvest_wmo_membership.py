"""Coverage for scripts/iwxxm/harvest_wmo_membership.py."""

from __future__ import annotations

from unittest.mock import patch

import pytest
import scripts.iwxxm.harvest_wmo_membership as harvest


@pytest.mark.unit
def test_main_writes_artifact(capsys: pytest.CaptureFixture[str]) -> None:
    out = (
        harvest._REPO
        / "packages/tac-validate/src/tac_validate/data/wmo_membership.json"
    )
    with (
        patch(
            "scripts.iwxxm.harvest_wmo_membership.write_membership_artifact",
            return_value=out,
        ) as write,
        patch("sys.argv", ["harvest_wmo_membership.py"]),
    ):
        assert harvest.main() == 0
    write.assert_called_once()
    assert "wmo_membership.json" in capsys.readouterr().out


@pytest.mark.unit
def test_main_custom_version() -> None:
    out = harvest._REPO / "artifact.json"
    with (
        patch(
            "scripts.iwxxm.harvest_wmo_membership.write_membership_artifact",
            return_value=out,
        ) as write,
        patch("sys.argv", ["harvest_wmo_membership.py", "--iwxxm-version", "2023-1"]),
    ):
        assert harvest.main() == 0
    write.assert_called_once_with(root=harvest._REPO, iwxxm_version="2023-1")
