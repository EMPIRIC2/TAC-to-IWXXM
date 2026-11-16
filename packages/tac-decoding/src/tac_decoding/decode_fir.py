"""Multi-word FIR proper-name span helpers.

[Corpus: product §F9]
"""

from __future__ import annotations

from tac_decoding.glossary import meaning_for

_FIR_NAME_STOP = frozenset({"FIR", "UIR", "FIR/UIR", "OCEANIC"})


def _fir_name_continuation_token(token: str) -> bool:
    """
    Return True when ``token`` may extend an open multi-word FIR name.

    Stops at FIR / UIR / OCEANIC markers and glossary-backed words so hazards
    and qualifiers are not absorbed into the name span.

    Parameters
    ----------
    token : str
        Next TAC token after a FIR-name head.

    Returns
    -------
    bool
        Whether the token continues the FIR proper name.
    """
    upper = token.upper()
    if upper in _FIR_NAME_STOP:
        return False
    head = upper.split("-", 1)[0]
    if meaning_for(head):
        return False
    letters = upper.replace("-", "")
    return bool(letters.isalpha() and len(upper) >= 2)


def _extend_fir_name_span(
    tokens: list[tuple[int, int, str]],
    index: int,
    *,
    tac: str,
) -> tuple[int, int, str, str, int] | None:
    """
    Join consecutive FIR-name words into one character span.

    Caller must have classified ``tokens[index]`` as a FIR name head. Lookahead
    stops before FIR / UIR / OCEANIC / glossary tokens.

    Parameters
    ----------
    tokens : list[tuple[int, int, str]]
        Token spans from :func:`_iter_tokens`.

    index : int
        Index of the first FIR-name token.

    tac : str
        Full TAC text (preserves original spacing in ``code``).

    Returns
    -------
    tuple[int, int, str, str, int] | None
        ``(start, end, code, explanation, token_count)`` when two or more name
        words join; ``None`` when only the head token applies.
    """
    if index >= len(tokens):
        return None
    start, end, first = tokens[index]
    parts = [first]
    last_end = end
    j = index + 1
    while j < len(tokens):
        _tok_start, tok_end, tok = tokens[j]
        if not _fir_name_continuation_token(tok):
            break
        parts.append(tok)
        last_end = tok_end
        j += 1
    if len(parts) < 2:
        return None
    display = " ".join(part.upper() for part in parts)
    return start, last_end, tac[start:last_end], f"FIR name ({display})", len(parts)
