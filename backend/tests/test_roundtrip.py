from gifts import metarDecoder, metarEncoder  # type: ignore
from _xml_utils import parse_xml, strip_dynamic_attrs, elements_equal
import backend.conversion as conv  # type: ignore
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
def test_decoder_encoder_pipeline_matches_expected(tac_path: pathlib.Path, xml_path: pathlib.Path) -> None:
    tac = _read_tac(tac_path)
    decoder = metarDecoder.Annex3()
    encoder = metarEncoder.Annex3()

    decoded = decoder(tac)
    xml_root = encoder(decoded, tac)
    assert xml_root is not None

    produced_xml = conv.ET.tostring(xml_root, encoding="unicode")
    exp_xml = xml_path.read_text(encoding="utf-8")

    prod_root = parse_xml(produced_xml)
    exp_root = parse_xml(exp_xml)
    strip_dynamic_attrs(prod_root)
    strip_dynamic_attrs(exp_root)

    assert elements_equal(prod_root, exp_root), f"Mismatch for {tac_path.name}"


@pytest.mark.skip(reason="XML→TAC reverse not supported in GIFTs; pending implementation")
def test_xml_to_tac_roundtrip_placeholder() -> None:
    pass
