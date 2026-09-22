"""TC-EV1210-002 — shadow XML stays byte-identical on every existing pin.

Compare every vendor example that is already on disk. Shadow must not change
convert XML. Do not fetch missing older copies. Do not delete legacy parsers
or the version matrix. [Corpus: tests] [Corpus: adr/ADR-045]
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tac2iwxxm.convert import convert
from tac2iwxxm.profile_registry import supported_iwxxm_versions_for_profile
from tac2iwxxm.shadow import convert_shadow

_REPO = Path(__file__).resolve().parents[3]
_VENDOR = _REPO / "vendor" / "schemas" / "iwxxm"
_PRODUCTS = Path(__file__).resolve().parents[1] / "src" / "tac2iwxxm" / "products"
_ALL_PINS = ("2023-1", "2025-2", "3.0.0")

# stem, product — SIGMET stays one product for ordinary / VA / TC examples.
_EXAMPLES = (
    ("metar-A3-1", "METAR"),
    ("taf-A5-2", "TAF"),
    ("airmet-A6-1a-TS", "AIRMET"),
    ("sigmet-A6-1a-TS", "SIGMET"),
    ("sigmet-VA-EGGX", "SIGMET"),
    ("sigmet-A6-2-TC", "SIGMET"),
    ("tc-advisory-A2-2", "TCA"),
    ("va-advisory-A7-2", "VAA"),
    ("spacewx-A7-3", "SWXA"),
    ("vona-A7-1", "VONA"),
)


def _pins_on_disk(stem: str) -> tuple[str, ...]:
    return tuple(pin for pin in _ALL_PINS if (_VENDOR / pin / "IWXXM" / "examples" / f"{stem}.xml").is_file())


def _tac_for(stem: str) -> str:
    for pin in ("2025-2", "2023-1", "3.0.0"):
        path = _VENDOR / pin / "IWXXM" / "examples" / f"{stem}.tac"
        if path.is_file():
            return path.read_text(encoding="utf-8")
    msg = f"missing vendor TAC peer for {stem}"
    raise FileNotFoundError(msg)


def test_delete_gate_pins_match_disk() -> None:
    """Do not invent pins. VAA / SWXA / VONA stay 2025-2 only."""
    expected = {
        "metar-A3-1": ("2023-1", "2025-2", "3.0.0"),
        "taf-A5-2": ("2023-1", "2025-2", "3.0.0"),
        "airmet-A6-1a-TS": ("2023-1", "2025-2", "3.0.0"),
        "sigmet-A6-1a-TS": ("2023-1", "2025-2", "3.0.0"),
        "sigmet-VA-EGGX": ("2023-1", "2025-2", "3.0.0"),
        "sigmet-A6-2-TC": ("2023-1", "2025-2", "3.0.0"),
        "tc-advisory-A2-2": ("2023-1", "2025-2", "3.0.0"),
        "va-advisory-A7-2": ("2025-2",),
        "spacewx-A7-3": ("2025-2",),
        "vona-A7-1": ("2025-2",),
    }
    for stem, pins in expected.items():
        assert _pins_on_disk(stem) == pins, stem


@pytest.mark.parametrize(("stem", "product"), _EXAMPLES)
@pytest.mark.parametrize("iwxxm_version", _ALL_PINS)
def test_shadow_xml_byte_identical_on_every_existing_pin(
    stem: str,
    product: str,
    iwxxm_version: str,
) -> None:
    pins = _pins_on_disk(stem)
    if iwxxm_version not in pins:
        pytest.skip(f"{stem} has no {iwxxm_version} vendor copy")
    tac = _tac_for(stem)
    legacy = convert(tac, product=product, profile="annex3", iwxxm_version=iwxxm_version)
    shadow = convert_shadow(tac, product=product, profile="annex3", iwxxm_version=iwxxm_version)
    assert shadow.ok is legacy.ok
    # Exact convert bytes — not a semantic / soft compare.
    assert shadow.xml == legacy.xml
    assert shadow.iwxxm_version == legacy.iwxxm_version
    assert shadow.profile == legacy.profile


def test_legacy_parsers_remain() -> None:
    slot = Path(__file__).resolve().parents[1] / "src" / "tac2iwxxm" / "slot_builders"
    for name in (
        "metar_speci.py",
        "taf.py",
        "sigmet_airmet.py",
        "vaa_tca.py",
        "swxa.py",
        "vona.py",
    ):
        assert (slot / name).is_file(), name
        assert not (_PRODUCTS / name).is_file(), name


def test_version_matrix_still_lists_profile_pins() -> None:
    annex3 = supported_iwxxm_versions_for_profile("annex3")
    assert "2023-1" in annex3
    assert "2025-2" in annex3
    assert "3.0.0" not in annex3
    ca = supported_iwxxm_versions_for_profile("ca_eccc")
    assert ca == frozenset({"3.0.0"})
