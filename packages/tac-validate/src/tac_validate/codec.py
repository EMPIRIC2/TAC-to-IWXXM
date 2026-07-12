"""Reusable msgspec JSON codec for LintReport (ADR-016)."""

from __future__ import annotations

import msgspec

from tac_validate.models import LintReport

json_encoder = msgspec.json.Encoder()
json_decoder = msgspec.json.Decoder(LintReport)

__all__ = ["json_decoder", "json_encoder"]
