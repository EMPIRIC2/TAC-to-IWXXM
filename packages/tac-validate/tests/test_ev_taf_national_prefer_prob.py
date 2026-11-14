"""EV-taf-national-prefer-prob — US/CA TAF prefix prefer + Annex 3 PROB nuance.

Default ``annex3`` + ICAO prefer maps US ``K*`` → ``iwxxm_us`` and Canadian
``CY*`` → ``ca_eccc`` for TAF (and METAR/SPECI/SIGMET when catalog-mapped).
Standalone PROB+period emits ``PROB_PRESENT`` info (emission of
``PROB_PERIOD_WITHOUT_TEMPO`` retired). Exact station maps (military / LatAm)
keep priority. ``CW*`` stays annex3 (no ``CW`` prefix). HKJK / LGTS keep
``INVALID_PROB`` because PROB qualifies BECMG/FM (Annex 3 App 5 §1.4).

[Corpus: product §F20] [Corpus: product §F36] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac_validate.api import lint, lint_with_profile, prefer_station_profile
from tac_validate.station_scoped_policy import resolve_profile_for_station

# US civilian K-prefix TAF with standalone PROB + period (no TEMPO), no BECMG.
_KSGF = "TAF KSGF 301720Z 3018/0124 18008KT P6SM SCT050 FM010000 20006KT P6SM SCT250 PROB30 0106/0112 2SM BR="
# Canadian CY-prefix TAF with standalone PROB + period.
_CYQT = "TAF CYQT 301738Z 3018/0118 27010KT P6SM SCT040 BECMG 3022/3024 32012KT PROB30 0100/0106 3SM -SHRA BR="
# UK EG-prefix TAF with standalone PROB + period.
_EGPF = "TAF EGPF 311100Z 3112/0118 24012KT 9999 SCT025 BECMG 3118/3121 20008KT PROB30 0103/0109 6000 RADZ BKN008="
# KDOV (Dover AFB) military form: QNH####INS + trailing TX/TN after change groups.
_KDOV = (
    "TAF KDOV 301800Z 3018/3124 30012KT 9999 FEW050 QNH3001INS "
    "BECMG 3100/3101 28009KT 9999 SCT050 QNH3005INS "
    "TX20/3019Z TN08/3111Z="
)
# HKJK / LGTS — PROB qualifies a change group (BECMG/FM): true defect.
_HKJK = "TAF HKJK 302300Z 3100/0106 02005KT 9999 BKN020 PROB30 BECMG 3114/3117 -RA FEW022CB BKN080="
_LGTS = "TAF LGTS 301700Z 3018/3118 32010KT 9999 FEW030 PROB30 BECMG 3020/3022 02012KT 4000 TSRA="


class TestIcaoPrefixResolve:
    def test_us_k_prefix_maps_to_iwxxm_us(self) -> None:
        assert resolve_profile_for_station("KORD") == "iwxxm_us"
        assert resolve_profile_for_station("KSGF") == "iwxxm_us"

    def test_canada_cy_prefix_maps_to_ca_eccc(self) -> None:
        assert resolve_profile_for_station("CYOW") == "ca_eccc"
        assert resolve_profile_for_station("CYQT") == "ca_eccc"

    def test_uk_eg_prefix_maps_to_uk_metoffice(self) -> None:
        assert resolve_profile_for_station("EGLL") == "uk_metoffice"
        assert resolve_profile_for_station("EGPF") == "uk_metoffice"

    def test_exact_military_station_beats_k_prefix(self) -> None:
        assert resolve_profile_for_station("KBIX") == "us_military"
        assert resolve_profile_for_station("KDOV") == "us_military"

    def test_latam_exact_unaffected(self) -> None:
        assert resolve_profile_for_station("SKBO") == "latam_taf"

    def test_canadian_cw_not_mapped(self) -> None:
        # Prefer is TAF-only and CW* is not a CY prefix; CW* METAR keeps annex3
        # errors (MANOBS VIS MISG / PRES MISG expected) — out of scope to soften.
        assert resolve_profile_for_station("CWDQ") is None

    def test_unmapped_station_stays_none(self) -> None:
        # No France / Brazil prefix profile; AU Y* now maps to au_bom
        # (EV-regional-profile-remainder C2). Standalone-PROB residual for
        # unmapped locales stays warning.
        assert resolve_profile_for_station("LFPG") is None
        assert resolve_profile_for_station("YPAD") == "au_bom"
        assert resolve_profile_for_station("SBPV") is None
        assert resolve_profile_for_station("") is None


class TestPreferStationProfile:
    def test_annex3_default_prefers_national(self) -> None:
        assert prefer_station_profile("annex3", "TAF", "KSGF") == "iwxxm_us"
        assert prefer_station_profile("annex3", "TAF", "CYQT") == "ca_eccc"
        assert prefer_station_profile("annex3", "TAF", "EGPF") == "uk_metoffice"

    def test_explicit_profile_honored(self) -> None:
        assert prefer_station_profile("iwxxm_us", "TAF", "CYQT") == "iwxxm_us"
        assert prefer_station_profile("ca_eccc", "TAF", "KSGF") == "ca_eccc"

    def test_prefer_metar_uses_national_when_mapped(self) -> None:
        assert prefer_station_profile("annex3", "METAR", "KSGF") == "iwxxm_us"
        # CW* has no catalog prefix — honesty: stay annex3 (no VIS/QNH soften).
        assert prefer_station_profile("annex3", "METAR", "CWDQ") == "annex3"


class TestProbPeriodInfoUnderPrefer:
    def test_us_k_prob_period_present(self) -> None:
        report = lint_with_profile(_KSGF, product="TAF", profile="annex3")
        assert "PROB_PERIOD_WITHOUT_TEMPO" not in {i.code for i in report.issues}
        assert any(i.code == "PROB_PRESENT" and i.severity == "info" for i in report.issues)
        assert report.ok is True

    def test_canada_cy_prob_period_present(self) -> None:
        report = lint_with_profile(_CYQT, product="TAF", profile="annex3")
        assert "PROB_PERIOD_WITHOUT_TEMPO" not in {i.code for i in report.issues}
        assert any(i.code == "PROB_PRESENT" and i.severity == "info" for i in report.issues)
        assert report.ok is True

    def test_uk_eg_prob_period_present(self) -> None:
        report = lint_with_profile(_EGPF, product="TAF", profile="annex3")
        assert "PROB_PERIOD_WITHOUT_TEMPO" not in {i.code for i in report.issues}
        assert any(i.code == "PROB_PRESENT" and i.severity == "info" for i in report.issues)
        assert report.ok is True

    def test_us_k_prob_period_present_without_prefer(self) -> None:
        # Direct lint (no prefer) also emits PROB_PRESENT — standalone is Annex 3-valid.
        report = lint(_KSGF, product="TAF", profile="annex3")
        assert "PROB_PERIOD_WITHOUT_TEMPO" not in {i.code for i in report.issues}
        assert any(i.code == "PROB_PRESENT" and i.severity == "info" for i in report.issues)


class TestKdovTxTn:
    def test_kdov_end_tx_tn_info_under_prefer(self) -> None:
        report = lint_with_profile(_KDOV, product="TAF", profile="annex3")
        assert not any(i.code == "INVALID_TX_TN" for i in report.issues)
        assert any(i.code == "TX_TN_PRESENT" for i in report.issues)
        assert report.ok is True

    def test_kdov_end_tx_tn_error_under_plain_annex3(self) -> None:
        report = lint(_KDOV, product="TAF", profile="annex3")
        assert any(i.code == "INVALID_TX_TN" and i.severity == "error" for i in report.issues)


class TestAnnex3ProbNuance:
    @pytest.mark.parametrize("tac", [_HKJK, _LGTS], ids=["HKJK", "LGTS"])
    def test_prob_qualifying_change_group_stays_error(self, tac: str) -> None:
        # PROB must not qualify BECMG/FM (Annex 3 App 5 §1.4). Prefer path must not
        # soften this; HK*/LG* are not mapped, so they stay annex3 regardless.
        report = lint_with_profile(tac, product="TAF", profile="annex3")
        assert report.ok is False
        assert any(i.code == "INVALID_PROB" and i.severity == "error" for i in report.issues)
