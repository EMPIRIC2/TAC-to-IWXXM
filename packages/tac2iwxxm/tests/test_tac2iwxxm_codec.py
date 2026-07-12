"""Codec reuse smoke tests for tac2iwxxm (ADR-016 / T1.4)."""

from __future__ import annotations

from tac2iwxxm.codec import json_decoder, json_encoder


def test_json_codec_roundtrip_reuses_module_instances() -> None:
    payload = {"ok": True, "n": 1}
    encoded = json_encoder.encode(payload)
    assert json_decoder.decode(encoded) == payload
    assert json_encoder is not None
    assert json_decoder is not None
