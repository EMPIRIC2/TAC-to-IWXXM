"""TC-EV023-004 - Dual-register colour + nil encode policy (S030 / EV-023 T4.1).

Locks offline vendor RDF/CSV as CI SoT for:
- ``49-2/AviationColourCode`` vs ``iwxxm/AviationColourCode`` member divergence
- dual nil SCH RDF (``common/nil`` + ``iwxxm/nil``)

Encode href policy helpers live in ``tac2iwxxm.codelists`` (T4.2).
No live codes.wmo.int HTML dependency.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_PIN_RULE = _REPO / "vendor" / "schemas" / "iwxxm" / "2025-2" / "IWXXM" / "rule"
_CSV_49_2 = (
    _REPO
    / "vendor"
    / "schemas"
    / "iwxxm-codelists"
    / "CSV"
    / "49-2"
    / "AviationColourCode"
    / "AviationColourCode_entity.csv"
)
_VENDOR_EX = _REPO / "vendor" / "schemas" / "iwxxm" / "2025-2" / "IWXXM" / "examples"
_AMD79_VAA = _REPO / "vendor" / "schemas" / "iwxxm-translation" / "Amd79-80-2023" / "volcanic-ash-advisory"

IWXXM_COLOUR_RDF = _PIN_RULE / "codes.wmo.int-iwxxm-AviationColourCode.rdf"
LEGACY_COLOUR_RDF = _PIN_RULE / "codes.wmo.int-49-2-AviationColourCode.rdf"
COMMON_NIL_RDF = _PIN_RULE / "codes.wmo.int-common-nil.rdf"
IWXXM_NIL_RDF = _PIN_RULE / "codes.wmo.int-iwxxm-nil.rdf"

IWXXM_COLOUR_PREFIX = "http://codes.wmo.int/iwxxm/AviationColourCode/"
LEGACY_COLOUR_PREFIX = "http://codes.wmo.int/49-2/AviationColourCode/"
COMMON_NIL_PREFIX = "http://codes.wmo.int/common/nil/"
IWXXM_NIL_PREFIX = "http://codes.wmo.int/iwxxm/nil/"

# Pin member sets (codes dig 2026-07-30; SCH RDF matches live).
IWXXM_COLOUR_MEMBERS = frozenset({"GREEN", "YELLOW", "ORANGE", "RED", "UNASSIGNED"})
LEGACY_COLOUR_MEMBERS = frozenset({"GREEN", "YELLOW", "ORANGE", "RED", "NIL", "NOT_GIVEN", "UNKNOWN"})
NIL_CONCEPT_NOTATIONS = frozenset(
    {
        "AboveDetectionRange",
        "BelowDetectionRange",
        "inapplicable",
        "missing",
        "noSignificantChange",
        "notDetectedByAutoSystem",
        "notObservable",
        "nothingOfOperationalSignificance",
        "template",
        "unknown",
        "withheld",
    }
)

_NOTATION = re.compile(r"<skos:notation>([^<]+)</skos:notation>")
_CONCEPT_ABOUT = re.compile(r'<skos:Concept rdf:about="([^"]+)"')
_COLOUR_HREF = re.compile(r'xlink:href="(https?://codes\.wmo\.int/[^"]*AviationColourCode/[^"]+)"')


def rdf_notations(path: Path) -> set[str]:
    """
    Return ``skos:notation`` values from an offline vendor RDF register file.

    Parameters
    ----------
    path : Path
        Path to a ``codes.wmo.int-*.rdf`` file under the pin.

    Returns
    -------
    set[str]
        Notation strings (includes the register's own notation when present).
    """
    text = path.read_text(encoding="utf-8")
    return set(_NOTATION.findall(text))


def rdf_concept_notations(path: Path, *, register_uri: str) -> set[str]:
    """
    Return concept notations whose ``rdf:about`` is under ``register_uri``.

    Parameters
    ----------
    path : Path
        Offline RDF path.
    register_uri : str
        Register base URI (no trailing slash), e.g. ``.../iwxxm/AviationColourCode``.

    Returns
    -------
    set[str]
        Member notations for concepts under the register.
    """
    text = path.read_text(encoding="utf-8")
    prefix = register_uri.rstrip("/") + "/"
    out: set[str] = set()
    for about in _CONCEPT_ABOUT.findall(text):
        if about.startswith(prefix):
            out.add(about[len(prefix) :])
    return out


def csv_49_2_colour_notations(path: Path) -> set[str]:
    """
    Return stable notations from the offline 49-2 AviationColourCode CSV.

    Parameters
    ----------
    path : Path
        ``AviationColourCode_entity.csv`` under ``iwxxm-codelists``.

    Returns
    -------
    set[str]
        Notation column values with ``status=stable``.
    """
    with path.open(encoding="utf-8", newline="") as fh:
        rows = csv.DictReader(fh)
        return {r["notation"] for r in rows if r.get("status") == "stable" and r.get("notation")}


def test_tc_ev023_004_offline_colour_and_nil_rdf_present() -> None:
    """Pin 2025-2 SCH RDF ships both colour registers and both nil registers."""
    for path in (IWXXM_COLOUR_RDF, LEGACY_COLOUR_RDF, COMMON_NIL_RDF, IWXXM_NIL_RDF):
        assert path.is_file(), f"missing offline SoT: {path}"
        resolved = str(path.resolve())
        assert "/vendor/schemas/" in resolved.replace("\\", "/")
        # SoT is local vendor bytes - not fetched at test time.
        assert path.stat().st_size > 0


def test_tc_ev023_004_offline_49_2_colour_csv_present() -> None:
    """Codelist CSV for 49-2 AviationColourCode is offline CI SoT (not live HTML)."""
    assert _CSV_49_2.is_file(), _CSV_49_2
    notations = csv_49_2_colour_notations(_CSV_49_2)
    assert notations == LEGACY_COLOUR_MEMBERS


def test_tc_ev023_004_iwxxm_colour_members_include_unassigned_not_legacy_nils() -> None:
    """``iwxxm/AviationColourCode`` has UNASSIGNED; not NIL/NOT_GIVEN/UNKNOWN."""
    members = rdf_concept_notations(
        IWXXM_COLOUR_RDF,
        register_uri="http://codes.wmo.int/iwxxm/AviationColourCode",
    )
    assert members == IWXXM_COLOUR_MEMBERS
    assert "UNASSIGNED" in members
    assert not {"NIL", "NOT_GIVEN", "UNKNOWN"} & members


def test_tc_ev023_004_legacy_49_2_colour_members_include_nil_not_unassigned() -> None:
    """``49-2/AviationColourCode`` has NIL/NOT_GIVEN/UNKNOWN; not UNASSIGNED."""
    members = rdf_concept_notations(
        LEGACY_COLOUR_RDF,
        register_uri="http://codes.wmo.int/49-2/AviationColourCode",
    )
    assert members == LEGACY_COLOUR_MEMBERS
    assert {"NIL", "NOT_GIVEN", "UNKNOWN"} <= members
    assert "UNASSIGNED" not in members
    # CSV and RDF must agree (offline dual SoT).
    assert csv_49_2_colour_notations(_CSV_49_2) == members


def test_tc_ev023_004_dual_nil_rdf_same_eleven_concepts() -> None:
    """``common/nil`` and ``iwxxm/nil`` expose the same 11 concept notations offline."""
    common = rdf_concept_notations(COMMON_NIL_RDF, register_uri="http://codes.wmo.int/common/nil")
    iwxxm = rdf_concept_notations(IWXXM_NIL_RDF, register_uri="http://codes.wmo.int/iwxxm/nil")
    assert common == NIL_CONCEPT_NOTATIONS
    assert iwxxm == NIL_CONCEPT_NOTATIONS
    assert common == iwxxm


def test_tc_ev023_004_vona_official_uses_iwxxm_colour_register() -> None:
    """2025-2 vona-A7-1 encodes colour under ``iwxxm/AviationColourCode`` (XSD vocabulary)."""
    xml = (_VENDOR_EX / "vona-A7-1.xml").read_text(encoding="utf-8")
    hrefs = _COLOUR_HREF.findall(xml)
    assert hrefs, "expected colour xlink:href in vona-A7-1"
    for href in hrefs:
        assert href.startswith(IWXXM_COLOUR_PREFIX), href
        assert not href.startswith(LEGACY_COLOUR_PREFIX), href
        token = href.rsplit("/", 1)[-1]
        assert token in IWXXM_COLOUR_MEMBERS


def test_tc_ev023_004_amd79_vaa_suite_may_lag_on_49_2_colour() -> None:
    """Amd79 VAA ``FVAU03ADRM-0424`` may use legacy 49-2 RED - suite lag, not 2025-2 target."""
    path = _AMD79_VAA / "FVAU03ADRM-0424.xml"
    assert path.is_file(), path
    xml = path.read_text(encoding="utf-8")
    hrefs = _COLOUR_HREF.findall(xml)
    assert any(h.startswith(LEGACY_COLOUR_PREFIX) for h in hrefs), hrefs
    # Our pin encode prefers iwxxm/ where XSD vocabulary says so (theme map).
    assert f"{IWXXM_COLOUR_PREFIX}RED" not in xml


def test_tc_ev023_004_policy_red_uses_iwxxm_register() -> None:
    """2025-2 colour encode maps RED → ``iwxxm/AviationColourCode/RED``."""
    from tac2iwxxm.codelists import aviation_colour_href

    href = aviation_colour_href("RED", iwxxm_version="2025-2")
    assert href == f"{IWXXM_COLOUR_PREFIX}RED"


@pytest.mark.parametrize(
    "token",
    ["UNKNOWN", "NOT GIVEN", "NOT_GIVEN", "NIL"],
)
def test_tc_ev023_004_policy_unassigned_tokens(token: str) -> None:
    """Legacy TAC colour tokens map to iwxxm UNASSIGNED under 2025-2 policy."""
    from tac2iwxxm.codelists import aviation_colour_href

    href = aviation_colour_href(token, iwxxm_version="2025-2")
    assert href == f"{IWXXM_COLOUR_PREFIX}UNASSIGNED"
    assert LEGACY_COLOUR_PREFIX not in href


@pytest.mark.parametrize(
    ("notation", "family", "prefix"),
    [
        ("missing", "common", COMMON_NIL_PREFIX),
        ("missing", "iwxxm", IWXXM_NIL_PREFIX),
        ("notObservable", "common", COMMON_NIL_PREFIX),
        ("withheld", "iwxxm", IWXXM_NIL_PREFIX),
    ],
)
def test_tc_ev023_004_policy_nil_family(notation: str, family: str, prefix: str) -> None:
    """Nil href policy selects ``common/nil`` or ``iwxxm/nil`` from offline registers."""
    from tac2iwxxm.codelists import nil_reason_href

    href = nil_reason_href(notation, family=family)  # type: ignore[arg-type]
    assert href == f"{prefix}{notation}"


def test_tc_ev023_004_policy_loads_offline_members() -> None:
    """Policy loader returns pin member sets without network I/O."""
    from tac2iwxxm.codelists import load_aviation_colour_members, load_nil_members

    assert load_aviation_colour_members("iwxxm", iwxxm_version="2025-2") == IWXXM_COLOUR_MEMBERS
    assert load_aviation_colour_members("49-2", iwxxm_version="2025-2") == LEGACY_COLOUR_MEMBERS
    assert load_nil_members("common", iwxxm_version="2025-2") == NIL_CONCEPT_NOTATIONS
    assert load_nil_members("iwxxm", iwxxm_version="2025-2") == NIL_CONCEPT_NOTATIONS


def test_tc_ev023_004_codelist_edge_errors_and_legacy_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover repo-root override, missing pin, unknown register/family, and 49-2 default."""
    from tac2iwxxm import codelists as cl

    cl.clear_codelist_caches()
    monkeypatch.setenv("TAC2IWXXM_REPO_ROOT", str(_REPO))
    assert cl.repo_root() == _REPO.resolve()

    with pytest.raises(FileNotFoundError, match=r".*"):
        cl.load_aviation_colour_members("iwxxm", iwxxm_version="no-such-pin")

    with pytest.raises(ValueError, match="unknown colour register"):
        cl.load_aviation_colour_members("bogus")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="unknown nil family"):
        cl.load_nil_members("bogus")  # type: ignore[arg-type]

    # Explicit 49-2 register keeps UNKNOWN (not remapped to iwxxm UNASSIGNED).
    href = cl.aviation_colour_href("UNKNOWN", iwxxm_version="2025-2", register="49-2")
    assert href == f"{LEGACY_COLOUR_PREFIX}UNKNOWN"

    # Non-2025-2 default register selection (still loads from that pin's rule dir).
    href_default = cl.aviation_colour_href("RED", iwxxm_version="2025-2", register=None)
    assert href_default == f"{IWXXM_COLOUR_PREFIX}RED"

    with pytest.raises(ValueError, match="colour notation"):
        cl.aviation_colour_href("PURPLE", iwxxm_version="2025-2")

    with pytest.raises(ValueError, match="nil notation"):
        cl.nil_reason_href("notANil", family="common")

    cl.clear_codelist_caches()
