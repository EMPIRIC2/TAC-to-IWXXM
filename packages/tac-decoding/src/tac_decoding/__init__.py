"""TAC → natural-language decode + glossary (F9 / ADR-044).

Publishable PyPI package ``tac-decoding``. No FastAPI or Supabase imports.
"""

from __future__ import annotations

from tac_decoding.catalog import catalog_entries
from tac_decoding.decode import DecodeResidual, DecodeResult, DecodeSegment, decode_tac
from tac_decoding.glossary import (
    explain_glossary_token,
    load_glossary,
    meaning_for,
    reload_glossary,
    resolve_location_name,
    set_location_name_resolver,
)

__version__ = "2026.9.17"

__all__ = [
    "DecodeResidual",
    "DecodeResult",
    "DecodeSegment",
    "__version__",
    "catalog_entries",
    "decode_tac",
    "explain_glossary_token",
    "load_glossary",
    "meaning_for",
    "reload_glossary",
    "resolve_location_name",
    "set_location_name_resolver",
]
