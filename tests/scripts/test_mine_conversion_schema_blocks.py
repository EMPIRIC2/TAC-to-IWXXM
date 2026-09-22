"""Tests for scripts/iwxxm/mine_conversion_schema_blocks.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "iwxxm" / "mine_conversion_schema_blocks.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "mine_conversion_schema_blocks", SCRIPT
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_mine_conversion_schema_blocks_check_ok() -> None:
    mod = _load_module()
    assert mod.main(["--check"]) == 0


def test_mine_conversion_schema_blocks_writes(tmp_path: Path) -> None:
    mod = _load_module()
    out = tmp_path / "blocks.yaml"
    assert mod.main(["--out", str(out)]) == 0
    assert out.is_file()
    assert "authority: wmo" in out.read_text(encoding="utf-8")


def test_mine_conversion_schema_blocks_check_missing(tmp_path: Path) -> None:
    mod = _load_module()
    missing = tmp_path / "missing.yaml"
    assert mod.main(["--check", "--out", str(missing)]) == 1


def test_mine_conversion_schema_blocks_check_drift(tmp_path: Path) -> None:
    mod = _load_module()
    drifted = tmp_path / "drifted.yaml"
    drifted.write_text("schema_version: 0\nblocks: []\n", encoding="utf-8")
    assert mod.main(["--check", "--out", str(drifted)]) == 1


def test_mine_xsd_skips_property_and_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _load_module()
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    empty = tmp_path / "Empty.xsd"
    empty.write_text(
        """<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element/>
  <xs:element name="METAR"/>
  <xs:element name="METAR"/>
  <xs:element name="FooProperty"/>
  <xs:element name="AbstractBar"/>
  <xs:complexType name="BazPropertyType"/>
</xs:schema>
""",
        encoding="utf-8",
    )
    # Nameless + duplicate + Property/Abstract leave only METAR once.
    block = mod._mine_xsd(
        empty,
        authority="wmo",
        qname_prefix="iwxxm",
        national_lines=["*"],
    )
    assert block is not None
    assert [c["xsd_name"] for c in block["cards"]] == ["METAR"]

    property_only = tmp_path / "PropertyOnly.xsd"
    property_only.write_text(
        """<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="FooProperty"/>
  <xs:element name="AbstractBar"/>
  <xs:complexType name="BazPropertyType"/>
</xs:schema>
""",
        encoding="utf-8",
    )
    assert (
        mod._mine_xsd(
            property_only,
            authority="wmo",
            qname_prefix="iwxxm",
            national_lines=["*"],
        )
        is None
    )


def test_mine_catalog_wmo_only_skips_missing_national(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When us/ca vendor dirs are absent, mine continues with WMO only."""
    mod = _load_module()
    vendor = tmp_path / "vendor"
    wmo = vendor / "iwxxm" / "2025-2" / "IWXXM"
    wmo.mkdir(parents=True)
    (wmo / "metar.xsd").write_text(
        """<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="METAR"/>
</xs:schema>
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(mod, "VENDOR", vendor)
    catalog = mod.mine_catalog()
    assert len(catalog["blocks"]) == 1
    assert catalog["blocks"][0]["authority"] == "wmo"


def test_mine_catalog_missing_wmo_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _load_module()
    monkeypatch.setattr(mod, "VENDOR", tmp_path / "no-vendor")
    with pytest.raises(FileNotFoundError, match="missing WMO"):
        mod.mine_catalog()


def test_tc_evpyl_mine_008_national_residuals_when_pins_absent() -> None:
    """TC-EVPYL-MINE-008: AU/BR/… lines listed as awaiting pins; check stays green."""
    mod = _load_module()
    missing = mod.awaiting_national_vendor_pins()
    for line in (
        "AU_BOM",
        "BR_DECEA",
        "HK_HKO",
        "IN_IMD",
        "JP_JMA",
        "KR_KMA",
        "NZ_CAA_MET",
        "UK_METOFFICE",
    ):
        assert line in missing
    assert "US_FAA_NWS" not in missing
    assert "CA_ECCC" not in missing
    catalog = mod.mine_catalog()
    residuals = catalog.get("national_residuals", {})
    awaiting = residuals.get("awaiting_vendor_pins", [])
    assert "AU_BOM" in awaiting
    assert mod.main(["--check"]) == 0


def test_mine_catalog_no_residuals_when_all_nationals_present(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When every expected national vendor dir exists, national_residuals is omitted."""
    mod = _load_module()
    vendor = tmp_path / "vendor"
    wmo = vendor / "iwxxm" / "2025-2" / "IWXXM"
    wmo.mkdir(parents=True)
    (wmo / "metar.xsd").write_text(
        """<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="METAR"/>
</xs:schema>
""",
        encoding="utf-8",
    )
    for _line, subdir, version, _auth, _qname in mod.NATIONAL_VENDOR_EXPECTATIONS:
        nd = vendor / subdir / version
        nd.mkdir(parents=True)
        (nd / "empty.xsd").write_text(
            """<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="SkipProperty"/>
</xs:schema>
""",
            encoding="utf-8",
        )
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(mod, "VENDOR", vendor)
    catalog = mod.mine_catalog()
    assert "national_residuals" not in catalog
    assert catalog["blocks"][0]["authority"] == "wmo"


def test_mine_catalog_skips_empty_national_xsds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Empty national XSDs are skipped (branch coverage for us/ca globs)."""
    mod = _load_module()
    vendor = tmp_path / "vendor"
    wmo = vendor / "iwxxm" / "2025-2" / "IWXXM"
    wmo.mkdir(parents=True)
    (wmo / "metar.xsd").write_text(
        """<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="METAR"/>
</xs:schema>
""",
        encoding="utf-8",
    )
    (wmo / "empty.xsd").write_text(
        """<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="SkipProperty"/>
</xs:schema>
""",
        encoding="utf-8",
    )
    for national in ("iwxxm-us", "iwxxm-ca"):
        nd = vendor / national / "3.0"
        nd.mkdir(parents=True)
        (nd / "empty.xsd").write_text(
            """<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="SkipProperty"/>
</xs:schema>
""",
            encoding="utf-8",
        )
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(mod, "VENDOR", vendor)
    catalog = mod.mine_catalog()
    assert len(catalog["blocks"]) == 1
    assert catalog["blocks"][0]["authority"] == "wmo"
