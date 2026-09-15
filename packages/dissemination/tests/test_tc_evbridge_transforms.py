"""TC-EVBRIDGE-008 — Dissemination library transforms (send paths only)."""

from __future__ import annotations

import pytest
from dissemination.collect_namespaces import is_collect_bulletin
from dissemination.transforms import (
    apply_dissemination_transforms,
    normalize_transform_steps,
)
from tac2iwxxm.library_assets import get_first_party_library_asset

_SAMPLE = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2" gml:id="m1">'
    "<iwxxm:observation/></iwxxm:METAR>"
)


def test_normalize_transform_steps_accepts_dicts_and_strings() -> None:
    steps = normalize_transform_steps(
        [
            {"id": "envelope", "type": "envelope"},
            "checksum",
        ]
    )
    assert [s.type for s in steps] == ["envelope", "checksum"]


def test_apply_transforms_envelope_and_checksum() -> None:
    seed = get_first_party_library_asset("LIB.DISSEMINATION.ICAO_2025")
    assert seed is not None
    result = apply_dissemination_transforms(
        _SAMPLE,
        seed.body["transforms"],
        bulletin_identifier="A_TEST.xml",
    )
    assert is_collect_bulletin(result.xml)
    assert "dissemination-checksum:" in result.xml
    assert "A_TEST.xml" in result.xml
    assert "envelope" in result.applied
    assert "checksum" in result.applied


def test_unknown_transform_type_fails_closed() -> None:
    with pytest.raises(ValueError, match="Unknown dissemination transform"):
        apply_dissemination_transforms(_SAMPLE, [{"type": "not_a_real_step"}])


def test_empty_transforms_is_noop() -> None:
    result = apply_dissemination_transforms(_SAMPLE, [])
    assert result.xml == _SAMPLE
    assert result.applied == ()
