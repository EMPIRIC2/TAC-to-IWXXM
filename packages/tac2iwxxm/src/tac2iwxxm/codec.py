"""Reusable msgspec JSON codec instances for hot paths (ADR-016).

Instantiate :class:`msgspec.json.Encoder` / :class:`msgspec.json.Decoder` once
and reuse them instead of constructing per call
(https://jcristharif.com/msgspec/perf-tips.html).
"""

from __future__ import annotations

import msgspec

json_encoder = msgspec.json.Encoder()
json_decoder = msgspec.json.Decoder()

__all__ = ["json_decoder", "json_encoder"]
