"""ADR-055 LintResolvePort + prefer beyond TAF (tac-validate evolve).

[Corpus: product §F15] [Corpus: product §F6] [Corpus: adr/ADR-055] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate.api import extract_station_icao, lint_with_profile, prefer_station_profile
from tac_validate.inherit_resolve import LintInheritResolver, catalog_inherit_root
from tac_validate.quality_policy_bind import resolve_tac_quality_policy_id

from metar_shared.inherit_factory import should_prefer_station


def test_prefer_metar_us_k_prefix() -> None:
    assert should_prefer_station(profile="annex3", product="METAR") is True
    assert prefer_station_profile("annex3", "METAR", "KSGF") == "iwxxm_us"


def test_prefer_speci_ca_cy_prefix() -> None:
    assert prefer_station_profile("annex3", "SPECI", "CYOW") == "ca_eccc"


def test_prefer_sigmet_when_icao_mapped() -> None:
    # Explicit station; SIGMET body may not yield CCCC via extract.
    assert prefer_station_profile("annex3", "SIGMET", "KJFK") == "iwxxm_us"


def test_prefer_skips_explicit_national() -> None:
    assert prefer_station_profile("ca_eccc", "METAR", "KSGF") == "ca_eccc"


def test_prefer_military_metar_falls_back_via_effective() -> None:
    # us_military is TAF-only; prefer remaps then effective_lint_profile → annex3.
    assert prefer_station_profile("annex3", "METAR", "KBIX") == "annex3"


def test_cw_metar_stays_annex3_honesty() -> None:
    assert prefer_station_profile("annex3", "METAR", "CWDQ") == "annex3"


def test_extract_station_icao_metar_speci() -> None:
    assert extract_station_icao("METAR KSGF 301755Z 18008KT 10SM SCT050 22/14 A3012=", "METAR") == "KSGF"
    assert extract_station_icao("SPECI CYOW 301812Z 27010KT 3SM -RA BKN012=", "SPECI") == "CYOW"
    # SIGMET / other products have no CCCC extractor in v1.
    assert extract_station_icao("YUDD SIGMET 2 VALID 101200/101600 YUSO-", "SIGMET") is None


def test_lint_resolve_port_bundle() -> None:
    port = LintInheritResolver()
    bundle = port.resolve_lint(product="METAR", profile="annex3", station="KORD")
    assert bundle.lint_profile_id == "iwxxm_us"
    assert bundle.product == "METAR"
    assert bundle.station == "KORD"
    assert bundle.tac_quality_policy_id == "annex3-metar-quality"
    assert any(part.startswith("lint:") for part in bundle.chain)


def test_quality_policy_taf_prob_period_info() -> None:
    assert resolve_tac_quality_policy_id("us_military", product="TAF") == "taf-prob-period-info-quality"
    assert resolve_tac_quality_policy_id("ca_eccc", product="TAF") == "taf-prob-period-info-quality"
    assert resolve_tac_quality_policy_id("uk_metoffice", product="TAF") == "taf-prob-period-info-quality"


def test_quality_policy_override() -> None:
    assert resolve_tac_quality_policy_id("annex3", product="TAF", tac_policy="annex3-taf-quality") == (
        "annex3-taf-quality"
    )


def test_catalog_inherit_root_product_country_station() -> None:
    root = catalog_inherit_root("TAF")
    assert root.id == "TAF"
    assert "iwxxm_us" in root.children
    assert "us_military" in root.children
    assert "KBIX" in root.children["us_military"].children
    assert "PTRO" in root.children["iwxxm_us"].children


def test_lint_with_profile_no_tac2iwxxm_import() -> None:
    # Behavioral lock: annex3 + US K* TAF emits PROB_PRESENT for standalone period.
    tac = "TAF KSGF 301720Z 3018/0124 18008KT P6SM SCT050 PROB30 0106/0112 2SM BR="
    report = lint_with_profile(tac, product="TAF", profile="annex3")
    assert "PROB_PERIOD_WITHOUT_TEMPO" not in {i.code for i in report.issues}
    assert any(i.code == "PROB_PRESENT" and i.severity == "info" for i in report.issues)


def test_invalid_prob_unchanged_under_prefer() -> None:
    # PROB qualifying BECMG remains a true defect (no soften).
    tac = "TAF HKJK 302300Z 3100/0106 02005KT 9999 BKN020 PROB30 BECMG 3114/3117 -RA FEW022CB BKN080="
    report = lint_with_profile(tac, product="TAF", profile="annex3")
    assert any(i.code == "INVALID_PROB" for i in report.issues)
