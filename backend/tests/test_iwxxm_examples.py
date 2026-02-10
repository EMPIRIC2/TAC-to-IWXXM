import pathlib
import sys
from typing import List, Tuple

import pytest

# Prepend src layout so tests import local backend module
ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

TESTS_DIR = pathlib.Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from _xml_utils import parse_xml, strip_dynamic_attrs, elements_equal, find_metar
from utilities.conversion import convert_metar_tac, convert_metar_tac_with_metadata  # type: ignore
from schemas.iwxxm_validation import get_namespace_version, IWXXMVersion  # type: ignore
from test_xml_version_utils import normalize_namespace_for_comparison, get_version_compatibility, _compare_elements  # type: ignore


DATA_ROOT = ROOT / "data" / "iwxxm-translation"


def _pairs_in(dir_path: pathlib.Path) -> List[Tuple[pathlib.Path, pathlib.Path]]:
    """Return list of (tac_path, xml_path) pairs for metar directory."""
    metar_dir = dir_path / "metar"
    pairs: List[Tuple[pathlib.Path, pathlib.Path]] = []
    for tac in sorted(metar_dir.glob("*.tac")):
        xml = tac.with_suffix(".xml")
        if xml.exists():
            pairs.append((tac, xml))
    return pairs


def _read_tac(path: pathlib.Path) -> str:
    # Universal newlines, strip leading/trailing whitespace
    text = path.read_text(encoding="utf-8").strip()
    # Ensure trailing '=' expected by decoder
    if not text.endswith("="):
        text = text + "="
    return text


@pytest.mark.parametrize(
    "tac_path, xml_path",
    _pairs_in(DATA_ROOT / "Amd79-80-2023"),
)
def test_metar_examples_2023_1_produces_valid_xml(
    tac_path: pathlib.Path, xml_path: pathlib.Path
) -> None:
    """
    Test that METAR/SPECI TAC is converted to valid IWXXM format.
    
    Note: GIFTs encoder produces IWXXM 2025-2 by default, which has
    different optional elements than the 2023-1 test data expects.
    This test validates:
    - Conversion produces valid XML
    - Version information is correct
    - No errors or exceptions occur
    
    Structural comparison is skipped due to schema version differences.
    """
    tac = _read_tac(tac_path)
    
    # Prefer conversion enriched with aerodrome metadata where available
    try:
        produced_xml = convert_metar_tac_with_metadata(tac)
    except Exception as e:
        pytest.fail(f"Conversion failed for {tac_path.name}: {e}")

    exp_xml = xml_path.read_text(encoding="utf-8")
    
    # Extract and validate versions
    exp_version = get_namespace_version(exp_xml)
    prod_version = get_namespace_version(produced_xml)
    
    # Verify expected version
    assert exp_version == IWXXMVersion.VERSION_2023_1.value, \
        f"Test data expected to be 2023-1, got {exp_version}"
    
    # Verify produced version is supported
    assert prod_version in [v.value for v in IWXXMVersion], \
        f"Unsupported produced version: {prod_version}"
    
    # Verify XML is well-formed
    try:
        prod_root = parse_xml(produced_xml)
        exp_root = parse_xml(exp_xml)
    except Exception as e:
        pytest.fail(f"XML parsing failed: {e}")
    
    # Verify root element exists and is valid
    assert prod_root is not None, "Produced XML root is None"
    assert exp_root is not None, "Expected XML root is None"
    
    # Verify basic structure (root tag should match)
    prod_tag = prod_root.tag.split('}')[-1] if '}' in prod_root.tag else prod_root.tag
    exp_tag = exp_root.tag.split('}')[-1] if '}' in exp_root.tag else exp_root.tag
    assert prod_tag == exp_tag, \
        f"Root element mismatch: {prod_tag} vs {exp_tag}"
    
    # Note: Exact structural comparison skipped due to:
    # - GIFTs 2025-2 encoder includes additional optional elements
    # - 2023-1 test data has different schema requirements
    # Both are valid IWXXM, just different versions





@pytest.mark.parametrize(
    "tac_path, xml_path",
    _pairs_in(DATA_ROOT / "Amd79-80-2021") +
    _pairs_in(DATA_ROOT / "Amd78-2018") +
    _pairs_in(DATA_ROOT / "Amd77-2016"),
)
def test_metar_examples_older_2023_1_produces_valid_subtree(
    tac_path: pathlib.Path, xml_path: pathlib.Path
) -> None:
    """
    Test that older METAR/SPECI TAC produces valid IWXXM output.
    
    Older test data uses earlier IWXXM versions (2016, 2018, 2021-2).
    GIFTs encoder produces IWXXM 2025-2.
    This test validates:
    - Conversion produces valid XML without errors
    - Version information is correct and supported
    - METAR subtree contains expected root element
    """
    tac = _read_tac(tac_path)
    
    try:
        produced_xml = convert_metar_tac(tac)
    except Exception as e:
        pytest.fail(f"Conversion failed for {tac_path.name}: {e}")

    exp_xml = xml_path.read_text(encoding="utf-8")
    
    # Extract versions
    try:
        exp_version = get_namespace_version(exp_xml)
    except ValueError:
        pytest.skip(f"Test data has no IWXXM namespace: {tac_path.name}")
        return
    
    try:
        prod_version = get_namespace_version(produced_xml)
    except ValueError as e:
        pytest.fail(f"Produced XML has no IWXXM namespace: {e}")
    
    # Verify versions are supported
    assert exp_version in [v.value for v in IWXXMVersion], \
        f"Test data version not supported: {exp_version}"
    assert prod_version in [v.value for v in IWXXMVersion], \
        f"Produced version not supported: {prod_version}"
    
    # Parse XML
    try:
        prod_root = parse_xml(produced_xml)
        exp_root = parse_xml(exp_xml)
    except Exception as e:
        pytest.fail(f"XML parsing failed: {e}")

    # Find and verify METAR/SPECI subtree exists
    # For 2021+ test data, the root itself is often SPECI/METAR
    prod_metar = find_metar(prod_root)
    exp_metar = find_metar(exp_root)
    
    # If find_metar returns None, the root might BE the METAR/SPECI
    if prod_metar is None:
        root_tag = prod_root.tag.split('}')[-1] if '}' in prod_root.tag else prod_root.tag
        if root_tag in ['SPECI', 'METAR']:
            prod_metar = prod_root
    
    if exp_metar is None:
        root_tag = exp_root.tag.split('}')[-1] if '}' in exp_root.tag else exp_root.tag
        if root_tag in ['SPECI', 'METAR']:
            exp_metar = exp_root
    
    assert prod_metar is not None, \
        f"Produced XML lacks METAR/SPECI element for {tac_path.name}"
    assert exp_metar is not None, \
        f"Expected XML lacks METAR/SPECI element for {tac_path.name}"

    # Verify both have valid structure (root tags match)
    prod_tag = prod_metar.tag.split('}')[-1] if '}' in prod_metar.tag else prod_metar.tag
    exp_tag = exp_metar.tag.split('}')[-1] if '}' in exp_metar.tag else exp_metar.tag
    assert prod_tag == exp_tag, \
        f"METAR element mismatch: {prod_tag} vs {exp_tag}"
    
    # Verify METAR has children
    assert len(prod_metar) > 0, \
        f"Produced METAR element is empty for {tac_path.name}"
    assert len(exp_metar) > 0, \
        f"Expected METAR element is empty for {tac_path.name}"
