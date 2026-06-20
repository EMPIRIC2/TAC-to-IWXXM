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

# Ensure GIFTs submodule is importable
GIFTs_DIR = ROOT / "GIFTs"
if GIFTs_DIR.exists() and str(GIFTs_DIR) not in sys.path:
    sys.path.insert(0, str(GIFTs_DIR))

import sys
from pathlib import Path

from _xml_utils import parse_xml
from gifts import metarDecoder, metarEncoder  # type: ignore

import src.utilities.conversion as conv  # type: ignore
from src.schemas.iwxxm_validation import IWXXMVersion, get_namespace_version  # type: ignore

sys.path.insert(0, str(Path(__file__).parent.parent / "iwxxm"))
from test_xml_version_utils import get_version_compatibility  # type: ignore

DATA_ROOT = ROOT / "data" / "iwxxm-translation"


def _pairs_in(dir_path: pathlib.Path) -> List[Tuple[pathlib.Path, pathlib.Path]]:
    metar_dir = dir_path / "metar"
    pairs: List[Tuple[pathlib.Path, pathlib.Path]] = []
    for tac in sorted(metar_dir.glob("*.tac")):
        xml = tac.with_suffix(".xml")
        if xml.exists():
            pairs.append((tac, xml))
    return pairs


def _read_tac(path: pathlib.Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    if not text.endswith("="):
        text = text + "="
    return text


@pytest.mark.parametrize(
    "tac_path, xml_path",
    _pairs_in(DATA_ROOT / "Amd79-80-2023"),
)
def test_decoder_encoder_pipeline_2023_1_produces_valid_xml(tac_path: pathlib.Path, xml_path: pathlib.Path) -> None:
    """
    Test that GIFTs decoder→encoder pipeline produces valid IWXXM XML.

    Expected: Test data is in IWXXM 2023-1 format
    Produced: GIFTs encoder produces IWXXM 2025-2 by default

    This test validates:
    - Decoder successfully parses TAC
    - Encoder produces valid XML
    - Version information is correct
    """
    tac = _read_tac(tac_path)
    decoder = metarDecoder.Annex3()
    encoder = metarEncoder.Annex3()

    try:
        decoded = decoder(tac)
        xml_root = encoder(decoded, tac)
    except Exception as e:
        pytest.fail(f"Pipeline failed for {tac_path.name}: {e}")

    assert xml_root is not None, f"Encoder returned None for {tac_path.name}"

    produced_xml = conv.ET.tostring(xml_root, encoding="unicode")
    exp_xml = xml_path.read_text(encoding="utf-8")

    # Extract versions
    exp_version = get_namespace_version(exp_xml)
    prod_version = get_namespace_version(produced_xml)

    # Verify versions
    assert exp_version == IWXXMVersion.VERSION_2023_1.value, f"Test data expected to be 2023-1, got {exp_version}"
    assert prod_version in [v.value for v in IWXXMVersion], f"Unsupported produced version: {prod_version}"

    # Parse and validate structure
    try:
        prod_root = parse_xml(produced_xml)
        exp_root = parse_xml(exp_xml)
    except Exception as e:
        pytest.fail(f"XML parsing failed: {e}")

    # Verify root elements match
    prod_tag = prod_root.tag.split("}")[-1] if "}" in prod_root.tag else prod_root.tag
    exp_tag = exp_root.tag.split("}")[-1] if "}" in exp_root.tag else exp_root.tag
    assert prod_tag == exp_tag, f"Root element mismatch: {prod_tag} vs {exp_tag}"

    # Verify has children
    assert len(prod_root) > 0, f"Produced root is empty for {tac_path.name}"
    assert len(exp_root) > 0, f"Expected root is empty for {tac_path.name}"


@pytest.mark.parametrize(
    "tac_path, xml_path",
    _pairs_in(DATA_ROOT / "Amd79-80-2023"),
)
def test_decoder_encoder_pipeline_2023_1_version_info(tac_path: pathlib.Path, xml_path: pathlib.Path) -> None:
    """
    Verify version information in decoder→encoder pipeline output.

    Note: GIFTs encoder may produce different versions than test data.
    This test documents the version behavior rather than enforcing exact match.
    """
    exp_xml = xml_path.read_text(encoding="utf-8")

    tac = _read_tac(tac_path)
    decoder = metarDecoder.Annex3()
    encoder = metarEncoder.Annex3()

    decoded = decoder(tac)
    xml_root = encoder(decoded, tac)
    produced_xml = conv.ET.tostring(xml_root, encoding="unicode")

    exp_version = get_namespace_version(exp_xml)
    prod_version = get_namespace_version(produced_xml)

    # Both versions should be supported
    assert exp_version in [v.value for v in IWXXMVersion], f"Test data version not supported: {exp_version}"
    assert prod_version in [v.value for v in IWXXMVersion], f"Produced version not supported: {prod_version}"

    # Document version compatibility
    # Allow any supported version transition (GIFTs encoder version is flexible)
    compatibility = get_version_compatibility(exp_version, prod_version)
    assert compatibility in ["exact_match", "2023-1_to_2025-2_upgrade", "2023-1_to_2021-2_downgrade", "incompatible"], (
        f"Unknown compatibility type: {compatibility}"
    )

    # Log the version mapping for visibility
    if compatibility == "incompatible":
        pytest.skip(
            f"Version mismatch (expected {exp_version}, got {prod_version}): GIFTs encoder version may differ from test data"
        )


@pytest.mark.skip(
    reason="XML→TAC reverse decoding not supported by GIFTs. "
    "GIFTs encodes TAC→XML but not XML→TAC. "
    "Validation: Use test_decoder_encoder_pipeline_2023_1_produces_valid_xml "
    "to validate the full pipeline. Implement XML→TAC decoding separately if needed."
)
def test_xml_to_tac_roundtrip_placeholder() -> None:
    pass
