"""TC-EV050-002 / AC2 - membership happy + unknown/sad (S059 / EV-050)."""

from __future__ import annotations

from pathlib import Path

import pytest
from tac_validate import membership

# (family, happy_notation, sad_notation)
_MATRIX: list[tuple[str, str, str]] = [
    ("weather_306_4678", "RA", "ZZWX"),
    ("present_or_forecast_weather", "+TSRA", "ZZWX"),
    ("recent_weather", "RERA", "REZZZZ"),
    ("cloud_amount", "BKN", "QQQ"),
    ("cloud_type", "CB", "XXX"),
    ("sigwx_phenomena", "VA", "FAKE_PHENOM"),
    ("airwx_phenomena", "ISOL_TS", "ISOL_ZZ"),
    ("nil_common", "missing", "notANilReason"),
    ("nil_common_rdf", "inapplicable", "notANilReason"),
]


@pytest.fixture(scope="module")
def sets() -> dict[str, frozenset[str]]:
    membership.load_membership_sets.cache_clear()
    return membership.load_membership_sets()


@pytest.mark.parametrize(("family", "happy", "sad"), _MATRIX)
def test_membership_happy_and_sad(
    sets: dict[str, frozenset[str]],
    family: str,
    happy: str,
    sad: str,
) -> None:
    assert membership.is_member(family, happy, sets=sets)
    assert not membership.is_member(family, sad, sets=sets)


def test_v1_families_present_in_artifact(sets: dict[str, frozenset[str]]) -> None:
    for key in membership.V1_FAMILY_KEYS:
        assert key in sets
        assert len(sets[key]) >= 1


def test_repo_root_default_without_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TAC_VALIDATE_REPO_ROOT", raising=False)

    assert membership.repo_root().name == "TAC-to-IWXXM"


def test_csv_notations_skips_blank_rows(tmp_path: Path) -> None:
    path = tmp_path / "members.csv"
    path.write_text("notation\n   \nRA\n", encoding="utf-8")

    assert membership._csv_notations(path) == frozenset({"RA"})


def test_rdf_notations_skips_other_registers(tmp_path: Path) -> None:
    path = tmp_path / "members.rdf"
    path.write_text(
        """<skos:Concept rdf:about="https://codes.wmo.int/other/value"/>
<skos:Concept rdf:about="https://codes.wmo.int/common/nil/missing"/>""",
        encoding="utf-8",
    )

    assert membership._rdf_notations(
        path,
        register_uri="https://codes.wmo.int/common/nil",
    ) == frozenset({"missing"})
