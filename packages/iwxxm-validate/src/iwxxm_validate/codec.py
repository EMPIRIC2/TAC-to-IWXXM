"""Reusable msgspec JSON codec instances (ADR-016)."""

from __future__ import annotations

import msgspec

from iwxxm_validate.models import ValidationReport

json_encoder = msgspec.json.Encoder()
json_decoder = msgspec.json.Decoder(ValidationReport)

__all__ = ["json_decoder", "json_encoder"]
