"""National advisory convert allowlist for issue 1270.

The runtime gate is package YAML. Catalog products for those emit keys match it.
Each listed centre converts the advisory from an existing public-shaped fixture.
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest
import yaml
from tac2iwxxm.convert_allowlist import (
    compose_allowlist,
    format_allowlist,
    load_convert_allowlist,
)

from tac2iwxxm import convert

_REPO = Path(__file__).resolve().parents[3]
_CATALOG = _REPO / "docs" / "domain" / "profiles" / "catalog.yaml"
_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"

_ROWS = (
    ("iwxxm_us", "VAA", _FIXTURES / "vaa_a7_2.tac"),
    ("au_bom", "SIGMET", _FIXTURES / "sigmet_a6_1a_ts.tac"),
    ("au_bom", "TCA", _FIXTURES / "tca_a2_2.tac"),
    ("au_bom", "SWXA", _FIXTURES / "swxa_a7_3.tac"),
    ("nz_caa_met", "VAA", _FIXTURES / "vaa_a7_2.tac"),
    ("nz_caa_met", "VONA", _FIXTURES / "vona_a7_1.tac"),
    ("uk_metoffice", "VAA", _FIXTURES / "vaa_a7_2.tac"),
    ("uk_metoffice", "SWXA", _FIXTURES / "swxa_a7_3.tac"),
    ("in_imd", "TCA", _FIXTURES / "tca_a2_2.tac"),
)


def test_catalog_products_match_package_allowlist() -> None:
    raw = yaml.safe_load(_CATALOG.read_text(encoding="utf-8"))
    allowlist = load_convert_allowlist()
    seen: set[str] = set()
    for row in raw["profiles"]:
        emit_key = str(row.get("emit_key", "")).lower()
        if emit_key not in allowlist:
            continue
        products = row.get("products")
        assert isinstance(products, list)
        codes = cast(list[object], products)
        assert frozenset(str(item).upper() for item in codes) == allowlist[emit_key]
        seen.add(emit_key)
    assert seen == set(allowlist)


def test_national_profiles_convert_published_advisories() -> None:
    for profile, product, path in _ROWS:
        result = convert(
            path.read_text(encoding="utf-8"),
            product=product,
            profile=profile,
            iwxxm_version="2025-2",
        )
        assert result.ok, (profile, product, result.issues)
        assert result.xml
        assert result.xml.lstrip().startswith("<")


def test_compose_clears_an_open_hydra_session() -> None:
    from hydra import initialize_config_dir
    from hydra.core.global_hydra import GlobalHydra

    from tac2iwxxm import convert_allowlist

    conf = Path(convert_allowlist.__file__).resolve().parent / "conf"
    if GlobalHydra.instance().is_initialized():
        GlobalHydra.instance().clear()
    initialize_config_dir(version_base="1.3", config_dir=str(conf))
    assert GlobalHydra.instance().is_initialized()
    assert "au_bom" in compose_allowlist()


def test_hydra_override_narrows_one_profile() -> None:
    narrowed = compose_allowlist(["profiles.au_bom=[METAR,TAF]"])
    assert narrowed["au_bom"] == frozenset({"METAR", "TAF"})
    assert "SIGMET" in load_convert_allowlist()["au_bom"]
    text = format_allowlist(narrowed)
    assert "au_bom: METAR, TAF" in text
    assert format_allowlist({}) == ""


def _not_a_mapping(*_args: object, **_kwargs: object) -> object:
    return ["nope"]


def test_compose_rejects_bad_profiles(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError, match="profiles must be a mapping"):
        compose_allowlist(["profiles=1"])
    with pytest.raises(ValueError, match="invalid allowlist row"):
        compose_allowlist(["profiles.au_bom=METAR"])
    monkeypatch.setattr(
        "tac2iwxxm.convert_allowlist.OmegaConf.to_container",
        _not_a_mapping,
    )
    with pytest.raises(ValueError, match="must be a mapping"):
        compose_allowlist()
