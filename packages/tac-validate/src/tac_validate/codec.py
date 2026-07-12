"""Reusable msgspec JSON codec instances for lint issue models (ADR-016).

Reuse module-level Encoder/Decoder instances on hot paths rather than
constructing new ones per encode/decode call.
"""

from __future__ import annotations

import msgspec

json_encoder = msgspec.json.Encoder()
json_decoder = msgspec.json.Decoder()

__all__ = ["json_decoder", "json_encoder"]
