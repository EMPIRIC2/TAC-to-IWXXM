"""CA_ECCC exchange output metadata for HTTP convert responses (EV-071 M2)."""

from __future__ import annotations

from tac2iwxxm import BulletinSplitError, split_bulletin
from tac2iwxxm.exchange_output import (
    build_ca_eccc_output_spec,
    issued_at_from_yygggg,
    profile_output_spec_to_dict,
)


def ca_eccc_output_spec_for_request(
    *,
    semantic_canonical: str,
    product: str,
    sample_text: str | None,
) -> dict[str, str] | None:
    """
    Build ``metadata.output_spec`` for CA_ECCC convert when bulletin context is available.

    Parameters
    ----------
    semantic_canonical :
        Resolved semantic profile id (lowercase registry key).
    product :
        API product enum.
    sample_text :
        First TAC or bulletin text from the request (may include an AHL line).

    Returns
    -------
    dict[str, str] | None
        Serialized output spec, or ``None`` when profile is not CA_ECCC.
    """
    if semantic_canonical != "ca_eccc":
        return None

    spec = build_ca_eccc_output_spec(product=product)
    if sample_text and sample_text.strip():
        try:
            split = split_bulletin(sample_text, product=product)
            from tac2iwxxm import parse_ahl

            parts = parse_ahl(split.meta.ahl)
            issued = issued_at_from_yygggg(parts.yygggg)
            spec = build_ca_eccc_output_spec(product=product, parts=parts, issued_at=issued)
        except BulletinSplitError:
            pass

    raw = profile_output_spec_to_dict(spec)
    return {key: str(value) for key, value in raw.items() if value is not None}


__all__ = ["ca_eccc_output_spec_for_request"]
