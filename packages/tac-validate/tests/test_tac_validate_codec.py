"""Codec reuse smoke tests for tac-validate (ADR-016 / T1.4)."""

from __future__ import annotations

from tac_validate import LintReport
from tac_validate.codec import json_decoder, json_encoder


def test_json_codec_roundtrip_reuses_module_instances() -> None:
    report = LintReport(ok=True, product="METAR", issues=[], fixes=[])
    encoded = json_encoder.encode(report)
    assert json_decoder.decode(encoded) == report
