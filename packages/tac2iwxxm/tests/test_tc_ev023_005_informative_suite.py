"""TC-EV023-005 - Amd79 TAC → 2025-2 → XSD+SCH informative suite (S030 / EV-023 T5.1).

Does **not** byte-match suite 2023-1 XML. Soft failures use
``@pytest.mark.xfail(strict=False)`` so main CI does not hard-fail (E23-T4=2).
SIGMET/AIRMET stay on official vendor 2025-2 examples (not in this suite).
"""

from __future__ import annotations

from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_AMD79 = _REPO / "vendor" / "schemas" / "iwxxm-translation" / "Amd79-80-2023"

IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

pytestmark = pytest.mark.iwxxm_translation_informative

_PRODUCT_DIRS: tuple[tuple[str, str], ...] = (
    ("metar", "auto"),  # METAR or SPECI from TAC lead
    ("taf", "TAF"),
    ("volcanic-ash-advisory", "VAA"),
    ("tropical-cyclone-advisory", "TCA"),
)


def _product_from_tac(tac: str, folder_hint: str) -> str:
    """
    Resolve F6 product for an Amd79 fixture.

    Parameters
    ----------
    tac : str
        TAC text.
    folder_hint : str
        Fixed product when not ``auto``.

    Returns
    -------
    str
        Product token for ``convert``.
    """
    if folder_hint != "auto":
        return folder_hint
    head = tac.lstrip()[:32].upper()
    if head.startswith("SPECI"):
        return "SPECI"
    return "METAR"


def _amd79_cases() -> list[tuple[str, Path, str]]:
    cases: list[tuple[str, Path, str]] = []
    for rel, hint in _PRODUCT_DIRS:
        root = _AMD79 / rel
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.tac")):
            product = _product_from_tac(path.read_text(encoding="utf-8"), hint)
            case_id = f"{rel}/{path.name}"
            cases.append((case_id, path, product))
    return cases


_CASES = _amd79_cases()


@pytest.mark.xfail(
    reason="EV-023 informative Amd79→2025-2 XSD+SCH (E23-T4=2 soft/xfail; no 2023-1 byte-match)",
    strict=False,
)
@pytest.mark.parametrize(
    ("case_id", "tac_path", "product"),
    _CASES,
    ids=[c[0] for c in _CASES],
)
def test_tc_ev023_005_amd79_convert_xsd_sch(case_id: str, tac_path: Path, product: str) -> None:
    """Amd79 TAC → our 2025-2 convert → XSD + Schematron (informative)."""
    from iwxxm_validate import validate

    from tac2iwxxm import convert

    assert tac_path.is_file(), tac_path
    tac = tac_path.read_text(encoding="utf-8")
    result = convert(
        tac,
        product=product,
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"{case_id}: convert failed: {result.issues!r}"
    assert result.xml is not None
    report = validate(
        result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in report.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, f"{case_id}: XSD/SCH blocking: {[(i.code, i.message[:120]) for i in blocking]}"
