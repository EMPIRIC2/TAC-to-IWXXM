"""Codec reuse smoke tests for tac-validate (ADR-016 / T1.4)."""

from __future__ import annotations

from tac_validate.codec import json_decoder, json_encoder


def test_json_codec_roundtrip_reuses_module_instances() -> None:
    payload = {"issues": [], "fixes": []}
    encoded = json_encoder.encode(payload)
    assert json_decoder.decode(encoded) == payload
