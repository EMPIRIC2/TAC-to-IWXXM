"""TAC → natural-language decode + glossary (F9).

Publishable PyPI package ``tac-decoding``. No FastAPI or Supabase imports.
"""

from __future__ import annotations

from tac_decoding.catalog import catalog_entries
from tac_decoding.decode import DecodeResidual, DecodeResult, DecodeSegment, decode_tac
from tac_decoding.dictionary import (
    dictionary_entries,
    dictionary_facets,
    filter_dictionary_entries,
    reload_dictionary_meta,
)
from tac_decoding.glossary import (
    explain_glossary_token,
    load_glossary,
    meaning_for,
    reload_glossary,
    resolve_location_name,
    set_location_name_resolver,
)
from tac_decoding.models.remarks import REMARK_FAMILIES, RemarkDecodeResult, RemarkGroup
from tac_decoding.remarks_decode import classify_remark_token, decode_remarks, segment_remarks

__version__ = "2026.11.5"

__all__ = [
    "REMARK_FAMILIES",
    "DecodeResidual",
    "DecodeResult",
    "DecodeSegment",
    "RemarkDecodeResult",
    "RemarkGroup",
    "__version__",
    "catalog_entries",
    "classify_remark_token",
    "decode_remarks",
    "decode_tac",
    "dictionary_entries",
    "dictionary_facets",
    "explain_glossary_token",
    "filter_dictionary_entries",
    "load_glossary",
    "meaning_for",
    "reload_dictionary_meta",
    "reload_glossary",
    "resolve_location_name",
    "segment_remarks",
    "set_location_name_resolver",
]
