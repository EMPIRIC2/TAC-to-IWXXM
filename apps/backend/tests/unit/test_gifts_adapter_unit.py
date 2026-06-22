"""Unit tests for gifts_adapter conversion wrappers and cache behavior."""

from __future__ import annotations

import sys
from types import ModuleType

import pytest

from src.utilities import gifts_adapter as ga


class _FakeAnnex3Encoder:
    def __init__(self, version=None):
        self.version = version
        self.calls = []

    def __call__(self, decoded_data, original_tac):
        self.calls.append((decoded_data, original_tac))
        return {"xml": "ok", "version": self.version}


class _FakeAnnex3Decoder:
    def __init__(self):
        self.calls = []

    def __call__(self, bulletin):
        self.calls.append(bulletin)
        return {"ident": {"str": "KJFK"}}


def test_wrap_in_bulletin_adds_keyword_and_equals():
    wrapped = ga._wrap_in_bulletin("KJFK 010000Z 00000KT CAVOK")

    assert wrapped.startswith("SAXX99 KWBC ")
    assert "\nMETAR KJFK 010000Z 00000KT CAVOK=" in wrapped


def test_wrap_in_bulletin_keeps_speci_prefix():
    wrapped = ga._wrap_in_bulletin("SPECI KJFK 010000Z 00000KT CAVOK=")

    assert "\nSPECI KJFK 010000Z 00000KT CAVOK=" in wrapped


def test_encoder_raises_when_metar_encoder_missing(monkeypatch):
    monkeypatch.setattr(ga, "metarEncoder", None)

    with pytest.raises(ImportError):
        ga.GIFTsEncoder(version="2025-2")


def test_decoder_raises_when_metar_decoder_missing(monkeypatch):
    monkeypatch.setattr(ga, "metarDecoder", None)

    with pytest.raises(ImportError):
        ga.GIFTsDecoder(version="2025-2")


def test_gifts_encoder_injects_metadata_for_dict_ident(monkeypatch):
    fake_encoder_module = type("E", (), {"Annex3": _FakeAnnex3Encoder})
    monkeypatch.setattr(ga, "metarEncoder", fake_encoder_module)

    class _GeoDB:
        def get(self, icao):
            if icao == "KJFK":
                return "John F Kennedy|JFK|KJFKA|40.0,-73.0"
            return None

    encoder = ga.GIFTsEncoder(version="2025-2", geo_locations_db=_GeoDB())
    decoded = {"ident": {"str": "KJFK", "extra": "x"}}

    result = encoder.encode(decoded, "METAR KJFK")

    assert result["xml"] == "ok"
    assert list(decoded["ident"].keys()) == ["str", "name", "alternate", "iataID", "position", "extra"]


def test_gifts_encoder_injects_metadata_for_list_ident(monkeypatch):
    fake_encoder_module = type("E", (), {"Annex3": _FakeAnnex3Encoder})
    monkeypatch.setattr(ga, "metarEncoder", fake_encoder_module)

    class _GeoDB:
        def get(self, icao):
            if icao == "KJFK":
                return "John F Kennedy|JFK|KJFKA|40.0,-73.0"
            return None

    encoder = ga.GIFTsEncoder(version="2025-2", geo_locations_db=_GeoDB())
    decoded = {"ident": [{"str": "KJFK", "extra": "x"}]}

    result = encoder.encode(decoded, "METAR KJFK")

    assert result["xml"] == "ok"
    assert list(decoded["ident"][0].keys()) == ["str", "name", "alternate", "iataID", "position", "extra"]


def test_gifts_decoder_wraps_tac_before_decoding(monkeypatch):
    fake_decoder_module = type("D", (), {"Annex3": _FakeAnnex3Decoder})
    monkeypatch.setattr(ga, "metarDecoder", fake_decoder_module)

    decoder = ga.GIFTsDecoder(version="2025-2")
    decoded = decoder.decode("METAR KJFK 010000Z 00000KT CAVOK")

    assert decoded["ident"]["str"] == "KJFK"
    assert decoder._decoder.calls
    assert decoder._decoder.calls[0].startswith("SAXX99 KWBC ")


def test_get_encoder_cache_and_clear(monkeypatch):
    fake_encoder_module = type("E", (), {"Annex3": _FakeAnnex3Encoder})
    monkeypatch.setattr(ga, "metarEncoder", fake_encoder_module)
    ga.clear_encoder_cache()

    db = object()
    first = ga.get_encoder("2025-2", geo_locations_db=db)
    second = ga.get_encoder("2025-2", geo_locations_db=db)

    assert first is second

    ga.clear_encoder_cache()
    third = ga.get_encoder("2025-2", geo_locations_db=db)
    assert third is not first


def test_get_decoder_singleton_and_reset(monkeypatch):
    fake_decoder_module = type("D", (), {"Annex3": _FakeAnnex3Decoder})
    monkeypatch.setattr(ga, "metarDecoder", fake_decoder_module)
    ga.reset_decoder()

    first = ga.get_decoder("2025-2")
    second = ga.get_decoder("2025-2")
    assert first is second

    ga.reset_decoder()
    third = ga.get_decoder("2025-2")
    assert third is not first


def test_convert_tac_to_iwxxm_adds_translator_fields(monkeypatch):
    class _FakeDecoder:
        def decode(self, _tac):
            return {"ident": {"str": "KJFK"}}

    class _FakeEncoder:
        def __init__(self):
            self.payload = None

        def encode(self, decoded, _tac):
            self.payload = decoded
            return {"encoded": True}

    fake_encoder = _FakeEncoder()

    monkeypatch.setattr(ga, "get_decoder", lambda _version=None: _FakeDecoder())
    monkeypatch.setattr(ga, "get_encoder", lambda _version=None, geo_locations_db=None: fake_encoder)

    gifts_module = ModuleType("gifts")
    common_module = ModuleType("gifts.common")
    xml_config_module = ModuleType("gifts.common.xmlConfig")
    xml_config_module.TRANSLATOR = True

    monkeypatch.setitem(sys.modules, "gifts", gifts_module)
    monkeypatch.setitem(sys.modules, "gifts.common", common_module)
    monkeypatch.setitem(sys.modules, "gifts.common.xmlConfig", xml_config_module)

    result = ga.convert_tac_to_iwxxm("METAR KJFK 010000Z 00000KT CAVOK", version="2025-2")

    assert result["encoded"] is True
    assert "translatedBulletinID" in fake_encoder.payload
    assert "translatedBulletinReceptionTime" in fake_encoder.payload


def test_convert_tac_to_iwxxm_ignores_translator_import_errors(monkeypatch):
    class _FakeDecoder:
        def decode(self, _tac):
            return {"ident": {"str": "KJFK"}}

    class _FakeEncoder:
        def encode(self, _decoded, _tac):
            return {"encoded": True}

    monkeypatch.setattr(ga, "get_decoder", lambda _version=None: _FakeDecoder())
    monkeypatch.setattr(ga, "get_encoder", lambda _version=None, geo_locations_db=None: _FakeEncoder())

    monkeypatch.delitem(sys.modules, "gifts.common", raising=False)
    monkeypatch.delitem(sys.modules, "gifts.common.xmlConfig", raising=False)

    result = ga.convert_tac_to_iwxxm("METAR KJFK 010000Z 00000KT CAVOK", version="2025-2")

    assert result["encoded"] is True


def test_encoder_metadata_missing_or_malformed_is_non_blocking(monkeypatch):
    fake_encoder_module = type("E", (), {"Annex3": _FakeAnnex3Encoder})
    monkeypatch.setattr(ga, "metarEncoder", fake_encoder_module)

    class _GeoDB:
        def __init__(self, value):
            self.value = value

        def get(self, _icao):
            return self.value

    encoder_none = ga.GIFTsEncoder(version="2025-2", geo_locations_db=_GeoDB(None))
    decoded_none = {"ident": {"str": "KJFK", "extra": "x"}}
    result_none = encoder_none.encode(decoded_none, "METAR KJFK")
    assert result_none["xml"] == "ok"
    assert list(decoded_none["ident"].keys()) == ["str", "extra"]

    encoder_bad = ga.GIFTsEncoder(version="2025-2", geo_locations_db=_GeoDB("bad|format"))
    decoded_bad = {"ident": {"str": "KJFK", "extra": "x"}}
    result_bad = encoder_bad.encode(decoded_bad, "METAR KJFK")
    assert result_bad["xml"] == "ok"
    assert list(decoded_bad["ident"].keys()) == ["str", "extra"]


def test_encoder_handles_non_dict_ident_list_item(monkeypatch):
    fake_encoder_module = type("E", (), {"Annex3": _FakeAnnex3Encoder})
    monkeypatch.setattr(ga, "metarEncoder", fake_encoder_module)

    class _GeoDB:
        def get(self, _icao):
            return "Name|IATA|ALT|10,20"

    encoder = ga.GIFTsEncoder(version="2025-2", geo_locations_db=_GeoDB())
    decoded = {"ident": ["KJFK"]}
    result = encoder.encode(decoded, "METAR KJFK")
    assert result["xml"] == "ok"


def test_encoder_init_failure_and_encode_failure(monkeypatch):
    class _BadAnnex3:
        def __init__(self, version=None):
            raise RuntimeError("init boom")

    bad_encoder_module = type("E", (), {"Annex3": _BadAnnex3})
    monkeypatch.setattr(ga, "metarEncoder", bad_encoder_module)

    with pytest.raises(RuntimeError):
        ga.GIFTsEncoder(version="2025-2")

    class _RaiseAnnex3:
        def __init__(self, version=None):
            pass

        def __call__(self, _decoded, _tac):
            raise RuntimeError("encode boom")

    raise_encoder_module = type("E2", (), {"Annex3": _RaiseAnnex3})
    monkeypatch.setattr(ga, "metarEncoder", raise_encoder_module)
    encoder = ga.GIFTsEncoder(version="2025-2")
    with pytest.raises(RuntimeError):
        encoder.encode({"ident": {"str": "KJFK"}}, "METAR KJFK")


def test_decoder_init_and_decode_failure(monkeypatch):
    class _BadDecoderInit:
        def __init__(self):
            raise RuntimeError("decoder init boom")

    bad_decoder_module = type("D", (), {"Annex3": _BadDecoderInit})
    monkeypatch.setattr(ga, "metarDecoder", bad_decoder_module)
    with pytest.raises(RuntimeError):
        ga.GIFTsDecoder(version="2025-2")

    class _BadDecoderCall:
        def __call__(self, _bulletin):
            raise RuntimeError("decoder boom")

    ok_decoder_module = type("D2", (), {"Annex3": lambda: _BadDecoderCall()})
    monkeypatch.setattr(ga, "metarDecoder", ok_decoder_module)
    decoder = ga.GIFTsDecoder(version="2025-2")
    with pytest.raises(RuntimeError):
        decoder.decode("METAR KJFK 010000Z 00000KT CAVOK")


def test_get_encoder_cache_key_differs_by_geo_db(monkeypatch):
    fake_encoder_module = type("E", (), {"Annex3": _FakeAnnex3Encoder})
    monkeypatch.setattr(ga, "metarEncoder", fake_encoder_module)
    ga.clear_encoder_cache()

    first = ga.get_encoder("2025-2", geo_locations_db=object())
    second = ga.get_encoder("2025-2", geo_locations_db=object())

    assert first is not second


def test_encoder_skips_metadata_when_ident_missing_icao(monkeypatch):
    fake_encoder_module = type("E", (), {"Annex3": _FakeAnnex3Encoder})
    monkeypatch.setattr(ga, "metarEncoder", fake_encoder_module)

    class _GeoDB:
        def get(self, _icao):
            return "Name|IATA|ALT|10,20"

    encoder = ga.GIFTsEncoder(version="2025-2", geo_locations_db=_GeoDB())
    decoded = {"ident": {"extra": "x"}}
    result = encoder.encode(decoded, "METAR KJFK")
    assert result["xml"] == "ok"
    assert decoded["ident"] == {"extra": "x"}


def test_encoder_skips_empty_metadata_parts(monkeypatch):
    fake_encoder_module = type("E", (), {"Annex3": _FakeAnnex3Encoder})
    monkeypatch.setattr(ga, "metarEncoder", fake_encoder_module)

    class _GeoDB:
        def get(self, _icao):
            return "||ALT|10,20"

    encoder = ga.GIFTsEncoder(version="2025-2", geo_locations_db=_GeoDB())
    decoded = {"ident": {"str": "KJFK"}}
    encoder.encode(decoded, "METAR KJFK")
    assert "name" not in decoded["ident"]
    assert "iataID" not in decoded["ident"]
    assert decoded["ident"]["alternate"] == "ALT"


def test_encoder_list_ident_with_string_element(monkeypatch):
    fake_encoder_module = type("E", (), {"Annex3": _FakeAnnex3Encoder})
    monkeypatch.setattr(ga, "metarEncoder", fake_encoder_module)

    class _GeoDB:
        def get(self, _icao):
            return "Name|IATA|ALT|10,20"

    encoder = ga.GIFTsEncoder(version="2025-2", geo_locations_db=_GeoDB())
    decoded = {"ident": ["KJFK"]}
    encoder.encode(decoded, "METAR KJFK")
    assert decoded["ident"][0] == "KJFK"


def test_encoder_metadata_injection_exception_is_non_blocking(monkeypatch):
    fake_encoder_module = type("E", (), {"Annex3": _FakeAnnex3Encoder})
    monkeypatch.setattr(ga, "metarEncoder", fake_encoder_module)

    class _BrokenGeoDB:
        def get(self, _icao):
            raise RuntimeError("geo db down")

    encoder = ga.GIFTsEncoder(version="2025-2", geo_locations_db=_BrokenGeoDB())
    decoded = {"ident": {"str": "KJFK"}}
    result = encoder.encode(decoded, "METAR KJFK")
    assert result["xml"] == "ok"


def test_convert_tac_to_iwxxm_uses_translation_time_when_present(monkeypatch):
    class _FakeDecoder:
        def decode(self, _tac):
            return {"ident": {"str": "KJFK"}, "translationTime": "2024-01-01T00:00:00Z"}

    class _FakeEncoder:
        def encode(self, decoded, _tac):
            return {"decoded": decoded}

    monkeypatch.setattr(ga, "get_decoder", lambda _version=None: _FakeDecoder())
    monkeypatch.setattr(ga, "get_encoder", lambda _version=None, geo_locations_db=None: _FakeEncoder())

    gifts_module = ModuleType("gifts")
    common_module = ModuleType("gifts.common")
    xml_config_module = ModuleType("gifts.common.xmlConfig")
    xml_config_module.TRANSLATOR = True
    monkeypatch.setitem(sys.modules, "gifts", gifts_module)
    monkeypatch.setitem(sys.modules, "gifts.common", common_module)
    monkeypatch.setitem(sys.modules, "gifts.common.xmlConfig", xml_config_module)

    result = ga.convert_tac_to_iwxxm("METAR KJFK 010000Z", version="2025-2")
    assert result["decoded"]["translatedBulletinReceptionTime"] == "2024-01-01T00:00:00Z"


def test_encoder_list_ident_with_empty_position_parts(monkeypatch):
    fake_encoder_module = type("E", (), {"Annex3": _FakeAnnex3Encoder})
    monkeypatch.setattr(ga, "metarEncoder", fake_encoder_module)

    class _GeoDB:
        def get(self, _icao):
            return "Name|IATA|ALT|"

    encoder = ga.GIFTsEncoder(version="2025-2", geo_locations_db=_GeoDB())
    decoded = {"ident": [{"str": "KJFK"}]}
    encoder.encode(decoded, "METAR KJFK")
    assert "position" not in decoded["ident"][0]


def test_encoder_list_ident_without_icao_skips_lookup(monkeypatch):
    fake_encoder_module = type("E", (), {"Annex3": _FakeAnnex3Encoder})
    monkeypatch.setattr(ga, "metarEncoder", fake_encoder_module)

    class _GeoDB:
        def get(self, _icao):
            return "Name|IATA|ALT|10,20"

    encoder = ga.GIFTsEncoder(version="2025-2", geo_locations_db=_GeoDB())
    decoded = {"ident": [{}]}
    result = encoder.encode(decoded, "METAR KJFK")
    assert result["xml"] == "ok"


def test_encoder_logs_when_metadata_lookup_returns_none(monkeypatch, caplog):
    import logging

    fake_encoder_module = type("E", (), {"Annex3": _FakeAnnex3Encoder})
    monkeypatch.setattr(ga, "metarEncoder", fake_encoder_module)

    class _GeoDB:
        def get(self, _icao):
            return None

    encoder = ga.GIFTsEncoder(version="2025-2", geo_locations_db=_GeoDB())
    decoded = {"ident": {"str": "KJFK"}}
    with caplog.at_level(logging.DEBUG, logger="src.utilities.gifts_adapter"):
        result = encoder.encode(decoded, "METAR KJFK")
    assert result["xml"] == "ok"
    assert "No metadata found for KJFK" in caplog.text


def test_convert_tac_to_iwxxm_skips_bulletin_id_without_ident_str(monkeypatch):
    class _FakeDecoder:
        def decode(self, _tac):
            return {"ident": {"index": 1}, "translationTime": "2024-01-01T00:00:00Z"}

    class _FakeEncoder:
        def encode(self, decoded, _tac):
            return {"decoded": decoded}

    monkeypatch.setattr(ga, "get_decoder", lambda _version=None: _FakeDecoder())
    monkeypatch.setattr(ga, "get_encoder", lambda _version=None, geo_locations_db=None: _FakeEncoder())

    gifts_module = ModuleType("gifts")
    common_module = ModuleType("gifts.common")
    xml_config_module = ModuleType("gifts.common.xmlConfig")
    xml_config_module.TRANSLATOR = True
    monkeypatch.setitem(sys.modules, "gifts", gifts_module)
    monkeypatch.setitem(sys.modules, "gifts.common", common_module)
    monkeypatch.setitem(sys.modules, "gifts.common.xmlConfig", xml_config_module)

    result = ga.convert_tac_to_iwxxm("METAR KJFK 010000Z", version="2025-2")
    assert "translatedBulletinID" not in result["decoded"]
    assert result["decoded"]["translatedBulletinReceptionTime"] == "2024-01-01T00:00:00Z"


def test_convert_tac_to_iwxxm_ignores_xmlconfig_attribute_error(monkeypatch):
    class _FakeDecoder:
        def decode(self, _tac):
            return {"ident": {"str": "KJFK"}}

    class _FakeEncoder:
        def encode(self, decoded, _tac):
            return {"decoded": decoded}

    monkeypatch.setattr(ga, "get_decoder", lambda _version=None: _FakeDecoder())
    monkeypatch.setattr(ga, "get_encoder", lambda _version=None, geo_locations_db=None: _FakeEncoder())

    gifts_module = ModuleType("gifts")
    common_module = ModuleType("gifts.common")
    common_module.xmlConfig = object()
    monkeypatch.setitem(sys.modules, "gifts", gifts_module)
    monkeypatch.setitem(sys.modules, "gifts.common", common_module)

    result = ga.convert_tac_to_iwxxm("METAR KJFK 010000Z", version="2025-2")
    assert "translatedBulletinID" not in result["decoded"]


def test_gifts_adapter_module_import_error_sets_none(monkeypatch):
    import builtins
    import importlib

    saved_decoder = ga.metarDecoder
    saved_encoder = ga.metarEncoder
    real_import = builtins.__import__

    def _fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "gifts" and level == 0:
            raise ImportError("gifts unavailable")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _fake_import)
    reloaded = importlib.reload(ga)
    assert reloaded.metarDecoder is None
    assert reloaded.metarEncoder is None
    ga.metarDecoder = saved_decoder
    ga.metarEncoder = saved_encoder
