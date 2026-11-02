"""Live 30d UNKNOWN_WMO_MEMBERSHIP residuals — keep as error after investigation.

- KCGI METAR ``-RABR`` is concatenated weather (should be ``-RA BR``); not in register.
- SIGMET ``MOD TURB`` is not in WMO SigWxPhenomena (register has ``SEV_TURB`` only);
  MOD TURB belongs on AIRMET — SIGMET misuse stays error.

Do not soften. [Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate import lint
from tac_validate.api import lint_with_profile

_KCGI_METAR = "METAR KCGI 011959Z 16007KT 6SM -RABR OVC006 15/15 A3020"
_FQBE_SIGMET = """WSMZ31 FQMA 021100
FQBE SIGMET A02 VALID 021126/021526  FQMA-
FQBE BEIRA FIR MOD TURB FCST WI S2619 E03142 - S2355 E03142 - S2443
E03407 - S2654 E03434 - S2619 E03142 TOP FL400=
"""
_SEV_TURB_OK = """WSMZ31 FQMA 021100
FQBE SIGMET A02 VALID 021126/021526  FQMA-
FQBE BEIRA FIR SEV TURB FCST WI S2619 E03142 - S2355 E03142 - S2443
E03407 - S2654 E03434 - S2619 E03142 TOP FL400=
"""


def test_kcgi_concatenated_rabr_emits_unknown_wmo_membership() -> None:
    report = lint_with_profile(
        _KCGI_METAR, product="METAR", profile="annex3", icao="KCGI"
    )
    membership = [i for i in report.issues if i.code == "UNKNOWN_WMO_MEMBERSHIP"]
    assert membership
    assert any("-RABR" in i.message for i in membership)
    assert all(i.severity == "error" for i in membership)


def test_sigmet_mod_turb_emits_unknown_wmo_membership() -> None:
    report = lint(_FQBE_SIGMET, product="SIGMET")
    membership = [i for i in report.issues if i.code == "UNKNOWN_WMO_MEMBERSHIP"]
    assert membership
    assert any("MOD TURB" in i.message for i in membership)
    assert all(i.severity == "error" for i in membership)


def test_sigmet_sev_turb_does_not_emit_membership_on_phenomenon() -> None:
    report = lint(_SEV_TURB_OK, product="SIGMET")
    membership = [i for i in report.issues if i.code == "UNKNOWN_WMO_MEMBERSHIP"]
    assert not any(
        "SEV TURB" in i.message or "SEV_TURB" in i.message for i in membership
    )
