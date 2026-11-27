"""Wire alias removal matrix after 2026-10-31 cutover (issue #1025).

Dimensions: success / failure x validation x mutate-equivalent resolve ops.
[Corpus: domain] [Corpus: product F35]
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tac2iwxxm.profile_registry import (
    known_semantic_profile_ids,
    resolve_semantic_profile,
)

from tac2iwxxm import convert

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
METAR = (FIXTURES / "metar_basic.tac").read_text(encoding="utf-8")


# --- Success paths ---


def test_s_convert_icao_2025_ok() -> None:
    result = convert(METAR, product="METAR", profile="ICAO_2025")
    assert result.ok
    assert result.deprecated_alias_used is False
    assert result.semantic_profile == "icao_2025"
    assert result.profile == "annex3"


def test_s_resolve_create_canonical() -> None:
    """Create-equivalent: resolve a canonical id (validation pass)."""
    resolved = resolve_semantic_profile("ICAO_2025")
    assert resolved is not None
    assert resolved.alias_used is False


# --- Failure / validation fail ---


@pytest.mark.parametrize("alias", ["annex3", "iwxxm_us"])
def test_f_v_alias_rejected_on_resolve(alias: str) -> None:
    assert resolve_semantic_profile(alias) is None
    assert alias not in known_semantic_profile_ids()


@pytest.mark.parametrize("alias", ["annex3", "iwxxm_us"])
def test_f_v_alias_rejected_on_convert(alias: str) -> None:
    result = convert(METAR, product="METAR", profile=alias)
    assert not result.ok
    assert result.issues[0].code == "UNSUPPORTED_PROFILE"


def test_f_unknown_profile_rejected() -> None:
    result = convert(METAR, product="METAR", profile="NOT_A_PROFILE")
    assert not result.ok
    assert result.issues[0].code == "UNSUPPORTED_PROFILE"


# --- Update-equivalent: re-resolve after canonical change ---


def test_m_update_canonical_stable() -> None:
    first = resolve_semantic_profile("ICAO_2025")
    second = resolve_semantic_profile("icao_2025")
    assert first == second


# --- Delete-equivalent: removed aliases no longer in known set ---


def test_m_delete_aliases_absent_from_known_ids() -> None:
    known = known_semantic_profile_ids()
    assert "annex3" not in known
    assert "iwxxm_us" not in known
    assert "icao_2025" in known
