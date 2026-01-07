from _xml_utils import parse_xml, strip_dynamic_attrs, elements_equal, find_metar
from backend.conversion import convert_metar_tac, convert_metar_tac_with_metadata  # type: ignore
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
def test_metar_examples_2023_strict(tac_path: pathlib.Path, xml_path: pathlib.Path) -> None:
    tac = _read_tac(tac_path)
    # Prefer conversion enriched with aerodrome metadata where available
    try:
        produced_xml = convert_metar_tac_with_metadata(tac)
    except Exception:
        produced_xml = convert_metar_tac(tac)

    exp_xml = xml_path.read_text(encoding="utf-8")
    prod_root = parse_xml(produced_xml)
    exp_root = parse_xml(exp_xml)

    # Strip dynamic attrs before structural compare
    strip_dynamic_attrs(prod_root)
    strip_dynamic_attrs(exp_root)

    assert elements_equal(prod_root, exp_root), f"Mismatch for {tac_path.name}"


@pytest.mark.parametrize(
    "tac_path, xml_path",
    _pairs_in(DATA_ROOT / "Amd79-80-2021") +
    _pairs_in(DATA_ROOT / "Amd78-2018") +
    _pairs_in(DATA_ROOT / "Amd77-2016"),
)
def test_metar_examples_older_relaxed(tac_path: pathlib.Path, xml_path: pathlib.Path) -> None:
    tac = _read_tac(tac_path)
    produced_xml = convert_metar_tac(tac)

    exp_xml = xml_path.read_text(encoding="utf-8")
    prod_root = parse_xml(produced_xml)
    exp_root = parse_xml(exp_xml)

    # Compare METAR subtree only, to avoid root-level namespace/version drift
    prod_metar = find_metar(prod_root)
    exp_metar = find_metar(exp_root)
    assert prod_metar is not None, "Produced XML lacks METAR element"
    assert exp_metar is not None, "Expected XML lacks METAR element"

    strip_dynamic_attrs(prod_metar)
    strip_dynamic_attrs(exp_metar)

    assert elements_equal(
        prod_metar, exp_metar), f"Subtree mismatch for {tac_path.name}"
