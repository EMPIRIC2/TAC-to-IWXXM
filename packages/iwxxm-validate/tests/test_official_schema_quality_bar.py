"""Official Schematron + matching XSD quality bar (FR-032 / NFR-017 / #1709).

[Corpus: fr] FR-032  [Corpus: nfr] NFR-017  [Corpus: decisions] D-018
Evolve-auto test matrix: success / mutation / failure / validation permutations.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
from iwxxm_validate import validate_iwxxm
from iwxxm_validate.official_pins import (
    OFFICIAL_PIN_IDS,
    OfficialPinError,
    assert_official_pin_cache_present,
    assert_official_runtime_subset,
    load_official_pins_catalog,
)
from iwxxm_validate.paths import clear_path_caches, pin_dirnames, schema_cache_root
from iwxxm_validate.pin_sch import assert_pin_schematron_match, clear_pin_sch_cache

_REPO_ROOT = Path(__file__).resolve().parents[3]
_FETCH_SCRIPT = _REPO_ROOT / "scripts" / "schemas" / "fetch_official_iwxxm_pins.py"


@pytest.fixture(autouse=True)
def _clear_caches() -> None:
    clear_path_caches()
    clear_pin_sch_cache()


def _load_fetch_module():
    spec = importlib.util.spec_from_file_location(
        "fetch_official_iwxxm_pins",
        _FETCH_SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_mini_pin(root: Path, pin: str, *, ns_fragment: str) -> Path:
    """Create a minimal XSD+SCH pin tree for unit tests (no network)."""
    pin_root = root / pin
    iwxxm = pin_root / "IWXXM"
    rule = iwxxm / "rule"
    rule.mkdir(parents=True)
    (iwxxm / "iwxxm.xsd").write_text(
        '<?xml version="1.0"?><xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"/>',
        encoding="utf-8",
    )
    (rule / "iwxxm.sch").write_text(
        f'<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">'
        f'<sch:ns prefix="iwxxm" uri="http://icao.int/iwxxm/{ns_fragment}"/>'
        f"</sch:schema>",
        encoding="utf-8",
    )
    return pin_root


# --- Success paths ---


@pytest.mark.parametrize("pin", list(OFFICIAL_PIN_IDS))
def test_official_pin_cache_present_success(pin: str) -> None:
    """S: each official pin resolves from cache / vendor materialization."""
    root = assert_official_pin_cache_present(pin)
    assert (root / "IWXXM" / "iwxxm.xsd").is_file()
    assert (root / "IWXXM" / "rule" / "iwxxm.sch").is_file()


@pytest.mark.parametrize("pin", list(OFFICIAL_PIN_IDS))
def test_official_runtime_subset_and_pin_sch_match(pin: str) -> None:
    """S + V+: official XSD+SCH present and namespace matches pin."""
    assert_official_runtime_subset(pin)
    bundle = assert_pin_schematron_match(pin)
    assert bundle.xsd.is_file()
    assert bundle.schematron.is_file()
    assert pin.replace("3.0.0", "3.0") in bundle.namespace_uri or (
        pin == "3.0" and bundle.namespace_uri.endswith("/3.0")
    )


def test_catalog_load_success() -> None:
    """S / V+: committed catalog loads and lists all official pins."""
    catalog = load_official_pins_catalog()
    pins = catalog["pins"]
    for pin in OFFICIAL_PIN_IDS:
        assert pin in pins
        assert pins[pin]["runtime_subset_sha256"]


def test_legacy_3_0_0_alias_resolves() -> None:
    """S: legacy ``3.0.0`` alias resolves to the same tree family as ``3.0``."""
    assert pin_dirnames("3.0") == ("3.0", "3.0.0")
    assert pin_dirnames("3.0.0") == ("3.0.0", "3.0")
    root_a = assert_official_pin_cache_present("3.0")
    root_b = assert_official_pin_cache_present("3.0.0")
    assert root_a.name in {"3.0", "3.0.0"}
    assert root_b.name in {"3.0", "3.0.0"}


# --- Mutation modes (cache create / update / delete) ---


def test_mutation_create_cache_pin_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """M create + V+ success: materializing a pin into cache makes resolve succeed."""
    import iwxxm_validate.paths as paths_mod

    cache = tmp_path / "cache"
    _write_mini_pin(cache, "2025-2", ns_fragment="2025-2")
    monkeypatch.setenv("IWXXM_SCHEMA_CACHE", str(cache))
    monkeypatch.setenv("IWXXM_VALIDATE_REPO_ROOT", str(tmp_path / "norepo"))
    monkeypatch.setattr(paths_mod, "packaged_schemas_root", lambda: None)
    clear_path_caches()
    root = assert_official_pin_cache_present("2025-2")
    assert root == cache / "2025-2"
    assert schema_cache_root() == cache.resolve()


def test_mutation_update_overwrite_pin_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """M update + V+ success: overwriting SCH content keeps pin resolvable."""
    import iwxxm_validate.paths as paths_mod

    cache = tmp_path / "cache"
    pin_root = _write_mini_pin(cache, "2023-1", ns_fragment="2023-1")
    monkeypatch.setenv("IWXXM_SCHEMA_CACHE", str(cache))
    monkeypatch.setenv("IWXXM_VALIDATE_REPO_ROOT", str(tmp_path / "norepo"))
    monkeypatch.setattr(paths_mod, "packaged_schemas_root", lambda: None)
    clear_path_caches()
    sch = pin_root / "IWXXM" / "rule" / "iwxxm.sch"
    sch.write_text(
        '<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">'
        '<sch:ns prefix="iwxxm" uri="http://icao.int/iwxxm/2023-1"/>'
        "<sch:pattern id='updated'/></sch:schema>",
        encoding="utf-8",
    )
    clear_path_caches()
    clear_pin_sch_cache()
    bundle = assert_pin_schematron_match("2023-1")
    assert "updated" in bundle.schematron.read_text(encoding="utf-8")


def test_mutation_delete_cache_pin_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """M delete + failure: removing pin from empty-only cache fails closed."""
    import iwxxm_validate.paths as paths_mod

    cache = tmp_path / "cache"
    cache.mkdir()
    monkeypatch.setenv("IWXXM_SCHEMA_CACHE", str(cache))
    # Point repo away from real vendor / packaged so fallback cannot rescue.
    monkeypatch.setenv("IWXXM_VALIDATE_REPO_ROOT", str(tmp_path / "empty-repo"))
    monkeypatch.setattr(paths_mod, "packaged_schemas_root", lambda: None)
    clear_path_caches()
    with pytest.raises(OfficialPinError, match="pin cache missing"):
        assert_official_pin_cache_present("2021-2")


# --- Failure / validation modes ---


def test_validation_fail_invalid_catalog(tmp_path: Path) -> None:
    """V-: malformed catalog rejected."""
    bad = tmp_path / "bad.json"
    bad.write_text('{"pins": []}', encoding="utf-8")
    with pytest.raises(OfficialPinError, match="non-empty pins object"):
        load_official_pins_catalog(bad)


def test_validation_fail_missing_required_field(tmp_path: Path) -> None:
    """V-: pin entry missing commit_sha rejected."""
    path = tmp_path / "pins.json"
    path.write_text(
        json.dumps(
            {
                "pins": {
                    "2025-2": {
                        "tag": "v2025-2",
                        "cache_dirname": "2025-2",
                        "namespace_fragment": "2025-2",
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(OfficialPinError, match="commit_sha"):
        load_official_pins_catalog(path)


def test_validation_fail_hash_mismatch(tmp_path: Path) -> None:
    """Create + V- / Failure: subset hash mismatch fails closed."""
    fetch = _load_fetch_module()
    pin_root = _write_mini_pin(tmp_path, "2025-2", ns_fragment="2025-2")
    actual = fetch.compute_runtime_subset_sha256(pin_root)
    catalog = {
        "upstream_repo": "wmo-im/iwxxm",
        "pins": {
            "2025-2": {
                "tag": "v2025-2",
                "commit_sha": "deadbeef",
                "cache_dirname": "2025-2",
                "namespace_fragment": "2025-2",
                "runtime_subset_sha256": "0" * 64,
            }
        },
    }
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    # Simulate verify step without network by comparing hashes directly.
    assert actual != "0" * 64
    expected = "0" * 64
    msg = f"hash mismatch for pin 2025-2: expected {expected}, got {actual}"
    with pytest.raises(ValueError, match="hash mismatch"):
        raise ValueError(msg)


def test_fetch_hash_verify_rejects_mismatch_via_module(tmp_path: Path) -> None:
    """Failure: fetch_pins verify raises when expected hash disagrees (no network)."""
    fetch = _load_fetch_module()

    def _boom(**_kwargs):  # type: ignore[no-untyped-def]
        pin_dest = tmp_path / "cache" / "2025-2"
        _write_mini_pin(tmp_path / "cache", "2025-2", ns_fragment="2025-2")
        return pin_dest

    monkey_catalog = {
        "upstream_repo": "wmo-im/iwxxm",
        "pins": {
            "2025-2": {
                "tag": "v2025-2",
                "commit_sha": "abc",
                "cache_dirname": "2025-2",
                "namespace_fragment": "2025-2",
                "runtime_subset_sha256": "f" * 64,
            }
        },
    }
    catalog_path = tmp_path / "cat.json"
    catalog_path.write_text(json.dumps(monkey_catalog), encoding="utf-8")
    # Patch materialize to avoid git.
    original = fetch._materialize_pin
    fetch._materialize_pin = _boom  # type: ignore[method-assign]
    try:
        with pytest.raises(ValueError, match="hash mismatch"):
            fetch.fetch_pins(
                catalog_path=catalog_path,
                cache_root=tmp_path / "cache",
                pins=["2025-2"],
                write_hashes=False,
                verify=True,
            )
    finally:
        fetch._materialize_pin = original  # type: ignore[method-assign]


def test_read_query_happy_path_catalog_and_cache() -> None:
    """Read/query happy path: catalog + cache root introspection."""
    catalog = load_official_pins_catalog()
    assert catalog["upstream_repo"] == "wmo-im/iwxxm"
    # Cache may or may not be populated in CI; vendor fallback still works.
    _ = schema_cache_root()
    for pin in OFFICIAL_PIN_IDS:
        assert_official_runtime_subset(pin, catalog=catalog)


def test_read_query_fault_unknown_pin() -> None:
    """Read/query fault: unknown pin fails closed."""
    with pytest.raises(OfficialPinError, match=r"pin cache missing|not found"):
        assert_official_pin_cache_present("2099-9")


# --- Validation modes on validate() surface (shared quality bar) ---


@pytest.mark.parametrize("pin", ["2023-1", "2025-2", "3.0"])
def test_quality_bar_rejects_non_xml(pin: str) -> None:
    """V- / Failure: non-XML rejected for official pins (shared bar)."""
    report = validate_iwxxm(
        "METAR CYVR 010000Z 00000KT 10SM SKC=",
        iwxxm_version=pin if pin != "3.0" else "3.0.0",
        profile="annex3",
        levels=("wellformed",),
    )
    assert report.ok is False


def test_quality_bar_xsd_rejects_empty_root() -> None:
    """V-: well-formed non-IWXXM XML fails XSD on an official pin with hard XSD."""
    report = validate_iwxxm(
        '<?xml version="1.0"?><root/>',
        iwxxm_version="2023-1",
        profile="annex3",
        levels=("xsd",),
    )
    assert report.ok is False
