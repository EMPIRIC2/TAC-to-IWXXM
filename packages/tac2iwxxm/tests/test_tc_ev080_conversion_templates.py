"""TC-EV080 — conversion template IR (package layer)."""

from __future__ import annotations

import pytest
from tac2iwxxm.conversion_templates import (
    compile_pattern,
    fork_first_party,
    get_first_party_template,
    list_first_party_templates,
    preview_bridge,
    reorder_slots,
    slot_from_dict,
    template_from_dict,
)


def test_list_first_party_includes_wind_cloud_vis() -> None:
    ids = {t.id for t in list_first_party_templates()}
    assert ids == {"CV.WIND", "CV.CLOUD", "CV.VIS"}


def test_compile_pattern_wind_pass_through() -> None:
    wind = get_first_party_template("CV.WIND")
    assert wind is not None
    pattern = compile_pattern(wind.slots)
    assert "{ddd:d3}" in pattern
    assert "{gust?:d2}" in pattern or "gust" in pattern


def test_reorder_slots_and_roundtrip_dict() -> None:
    wind = get_first_party_template("CV.WIND")
    assert wind is not None
    reordered = reorder_slots(wind.slots, "uom", "ddd")
    assert reordered[0].id == "uom"
    raw = wind.to_dict()
    again = template_from_dict(raw)
    assert again.id == wind.id
    assert again.slots[0].id == wind.slots[0].id
    slot = slot_from_dict({"id": "x", "label": "x", "type": "digits", "digits": 2})
    assert slot.digits == 2


def test_preview_bridge_wind_matched() -> None:
    wind = get_first_party_template("CV.WIND")
    assert wind is not None
    preview = preview_bridge(wind, focus_group="18012G20KT")
    assert preview.matched is True
    assert any(c["slot"] == "direction" and c["value"] == "180" for c in preview.captures)
    assert "WindObservation" in preview.xml_block
    assert "gustSpeed" in preview.xml_block


def test_preview_bridge_wind_no_gust() -> None:
    wind = get_first_party_template("CV.WIND")
    assert wind is not None
    preview = preview_bridge(wind, focus_group="18012KT")
    assert preview.matched is True
    assert "gust omitted" in preview.xml_block


def test_fork_first_party_custom_access() -> None:
    forked = fork_first_party("CV.WIND", new_id="custom-1", name="My wind")
    assert forked.access == "custom"
    assert forked.fork_of == "CV.WIND"
    assert forked.name == "My wind"
    with pytest.raises(KeyError):
        fork_first_party("CV.NOPE", new_id="x")
