"""Coverage for annex3_emit shared helpers (EV-037 TD-2)."""

from __future__ import annotations

import pytest
from tac2iwxxm.profiles.annex3_emit._common import (
    _fmt_coord,
    _ns,
    _sigmet_phenomenon_href,
)


def test_annex3_emit_ns_known_versions() -> None:
    assert _ns("2025-2") == "http://icao.int/iwxxm/2025-2"
    assert _ns("2023-1") == "http://icao.int/iwxxm/2023-1"
    assert _ns("3.0.0") == "http://icao.int/iwxxm/3.0"


def test_annex3_emit_ns_unknown_version_raises() -> None:
    with pytest.raises(ValueError, match="unsupported iwxxm_version"):
        _ns("2099-9")


def test_annex3_emit_fmt_coord() -> None:
    assert _fmt_coord(12.0) == "12"
    assert _fmt_coord(12.34) == "12.34"


def test_sigmet_phenomenon_href_sigwx_vs_airwx() -> None:
    """SigWx codes stay on SigWxPhenomena; AIRMET vocab uses AirWxPhenomena."""
    assert _sigmet_phenomenon_href("SEV_MTW").endswith("SigWxPhenomena/SEV_MTW")
    assert _sigmet_phenomenon_href("OCNL_TS").endswith("AirWxPhenomena/OCNL_TS")
    assert _sigmet_phenomenon_href("").endswith("AirWxPhenomena/")
