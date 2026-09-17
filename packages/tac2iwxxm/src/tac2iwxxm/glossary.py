"""Compatibility shim — glossary implementation lives in ``tac_decoding`` (ADR-044).

Replaces this module object with ``tac_decoding.glossary`` so private helpers remain
importable for one release. Prefer ``from tac_decoding import load_glossary``.
"""

from __future__ import annotations

import sys

from tac_decoding import glossary as _impl
from tac_decoding.glossary import explain_glossary_token as explain_glossary_token
from tac_decoding.glossary import load_glossary as load_glossary
from tac_decoding.glossary import meaning_for as meaning_for
from tac_decoding.glossary import reload_glossary as reload_glossary
from tac_decoding.glossary import resolve_location_name as resolve_location_name
from tac_decoding.glossary import set_location_name_resolver as set_location_name_resolver

__all__ = [
    "explain_glossary_token",
    "load_glossary",
    "meaning_for",
    "reload_glossary",
    "resolve_location_name",
    "set_location_name_resolver",
]

sys.modules[__name__] = _impl
