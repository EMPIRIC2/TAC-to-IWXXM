"""Pre-normalization of METAR TAC text before strict GIFTs lexer parsing.

Handles common non-standard recent weather tokens that appear in manual METAR
input but are rejected by the strict WMO METAR lexer (GIFTs).

Background
----------
The GIFTs ``rewx`` token rule requires a phenomenon after the optional descriptor:
    ``RE(FZ|SH|TS)?(DZ|RASN|RA|...UP|//)``

So ``RESH`` (descriptor only, no phenomenon) fails lexing, while ``RESHRA``
(descriptor + phenomenon) succeeds.  WMO code table D-6 includes ``RESHUP``
and ``REFZUP`` as valid recent-weather codes.  Appending ``UP`` (unidentified
precipitation) converts a truncated descriptor-only token into a standards-
recognised token without inventing specific meteorology.

This normalizer is applied **before** the GIFTs decoder in lenient mode so
that the rest of the conversion pipeline continues unchanged.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

# Matches exactly RE + descriptor (SH or FZ) with nothing after — these are
# the only descriptor-only tokens that are both (a) observed in the wild and
# (b) fixable via a standards-conformant UP suffix.
_TRUNCATED_REWX_RE = re.compile(r"^RE(SH|FZ)$", re.IGNORECASE)


def normalize_recent_weather_tokens(
    tac_text: str,
) -> Tuple[str, List[Dict[str, Any]]]:
    """Rewrite truncated recent-weather tokens to WMO D-6 compliant forms.

    Operates at the token (whitespace-delimited word) level so that valid
    tokens such as ``RESHRA``, ``VCSH``, and ``SHRA`` are never modified.

    Rewrites applied (exact token match only):
        ``RESH``  →  ``RESHUP``   (rule: ``recent_weather_truncated_showers``)
        ``REFZ``  →  ``REFZUP``   (rule: ``recent_weather_truncated_freezing``)

    Args:
        tac_text: Raw METAR/SPECI TAC string (with or without WMO header).

    Returns:
        A two-tuple ``(normalized_text, warnings)`` where ``warnings`` is a
        list of dicts with keys ``index``, ``original``, ``replacement``, and
        ``rule``.  The list is empty when no rewrites were made.
    """
    warnings: List[Dict[str, Any]] = []

    # Preserve leading/trailing whitespace on the outer string but work on
    # individual tokens so we don't alter separators inside the message.
    stripped = tac_text.strip()
    if not stripped:
        return tac_text, warnings

    # Split into alternating tokens and whitespace so we can rewrite only
    # tokens while preserving all original separators exactly.
    parts = re.split(r"(\s+)", stripped)
    token_index = 0

    for i, part in enumerate(parts):
        # Odd entries are captured separators from the split regex.
        if i % 2 == 1:
            continue

        token = part
        # Some parsers/users append '=' to the last token; strip it before
        # matching so we can still recognise e.g. 'RESH=' as a RESH token.
        trailing_eq = token.endswith("=")
        bare = token[:-1] if trailing_eq else token
        upper_bare = bare.upper()

        match = _TRUNCATED_REWX_RE.match(upper_bare)
        if match:
            descriptor = match.group(1).upper()
            replacement_bare = f"RE{descriptor}UP"
            replacement = replacement_bare + ("=" if trailing_eq else "")

            rule = "recent_weather_truncated_showers" if descriptor == "SH" else "recent_weather_truncated_freezing"

            warnings.append(
                {
                    "index": token_index,
                    "original": token,
                    "replacement": replacement,
                    "rule": rule,
                }
            )
            parts[i] = replacement

        token_index += 1

    normalized = "".join(parts)
    # Re-attach any leading/trailing whitespace from the original input so we
    # don't silently alter strings that the caller may be sensitive about.
    leading = tac_text[: len(tac_text) - len(tac_text.lstrip())]
    trailing = tac_text[len(tac_text.rstrip()) :]
    return leading + normalized + trailing, warnings


def normalize_recent_weather_for_tac(
    tac_text: str,
) -> Tuple[str, List[Dict[str, Any]]]:
    """Centralized wrapper for TAC recent-weather normalization."""
    return normalize_recent_weather_tokens(tac_text)
