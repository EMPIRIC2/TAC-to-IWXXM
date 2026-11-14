""" ConvertResolvePort for tac2iwxxm (emit/policy prefer).

Pin / IWXXM version selection is unchanged — this covers emit + policy ids only.
[Corpus: product §F6] [Corpus: pack-engine-boundary]
"""

from __future__ import annotations

import pytest
from tac2iwxxm.convert import convert
from tac2iwxxm.convert_resolve import ConvertInheritResolver, prefer_emit_profile
from tac2iwxxm.profile_resolve import resolve_validation_policies

from metar_shared.inherit_factory import should_prefer_station


def test_should_prefer_default_metar() -> None:
    assert should_prefer_station(profile="annex3", product="METAR") is True
    assert should_prefer_station(profile="iwxxm_us", product="METAR") is False


def test_prefer_emit_cy_metar_to_ca_eccc() -> None:
    assert prefer_emit_profile("annex3", "METAR", "CYUL") == "ca_eccc"
    assert prefer_emit_profile("annex3", "METAR", "CWDQ") == "annex3"


def test_prefer_emit_explicit_profile_wins() -> None:
    assert prefer_emit_profile("iwxxm_us", "METAR", "CYUL") == "iwxxm_us"


def test_prefer_emit_without_tac_validate_keeps_emit(monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins

    real_import = builtins.__import__

    def _blocked(name: str, *args: object, **kwargs: object) -> object:
        if name == "tac_validate.inherit_resolve":
            raise ImportError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked)
    assert prefer_emit_profile("annex3", "METAR", "CYUL") == "annex3"


def test_prefer_emit_does_not_change_pin_binding() -> None:
    # Policy bind for preferred emit still uses annex3-family IWXXM output id;
    # version pins remain outside this resolver.
    policies = resolve_validation_policies("ca_eccc", product="METAR")
    assert policies.iwxxm_output_policy_id == "annex3-iwxxm-output"
    assert policies.emit_key == "ca_eccc"


def test_convert_resolve_port_bundle() -> None:
    port = ConvertInheritResolver()
    bundle = port.resolve_convert(product="METAR", profile="annex3", station="CYUL")
    assert bundle.product == "METAR"
    assert bundle.station == "CYUL"
    assert bundle.emit_key == "ca_eccc"
    assert bundle.lint_profile_id == "ca_eccc"
    assert bundle.tac_quality_policy_id == "annex3-metar-quality"
    assert bundle.iwxxm_output_policy_id == "annex3-iwxxm-output"
    assert any(part.startswith("emit:") for part in bundle.chain)


def test_convert_resolve_taf_prob_period_info() -> None:
    port = ConvertInheritResolver()
    bundle = port.resolve_convert(product="TAF", profile="annex3", station="KSGF")
    assert bundle.emit_key == "iwxxm_us"
    assert bundle.tac_quality_policy_id == "taf-prob-period-info-quality"


def test_convert_does_not_auto_prefer_annex3_station() -> None:
    # convert() must keep explicit annex3 (no silent national remap / pin rewrite).
    tac = "METAR CYUL 231800Z 24010KT 15SM FEW040 14/13 A2995="
    result = convert(tac, product="METAR", profile="annex3")
    assert result.profile == "annex3"
