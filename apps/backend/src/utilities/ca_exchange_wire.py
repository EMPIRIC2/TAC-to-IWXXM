"""CA_ECCC exchange output metadata for HTTP convert responses (EV-071 M2 / EV-073 M1)."""

from __future__ import annotations

from tac2iwxxm.ca_collect_packaging import wrap_ca_eccc_collect
from tac2iwxxm.exchange_output import (
    build_ca_eccc_output_spec,
    ca_msc_filename,
    issued_at_from_yygggg,
    profile_output_spec_to_dict,
)

from tac2iwxxm import BulletinSplitError, parse_ahl, split_bulletin


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


def ca_collect_bulletin_identifier(*, product: str, tac_input: str | None) -> str | None:
    """
    Derive MSC datamart filename for COLLECT ``bulletinIdentifier``.

    Parameters
    ----------
    product :
        API product enum.
    tac_input :
        Source TAC (may include WMO AHL line).

    Returns
    -------
    str | None
        MSC filename when AHL context is parseable; otherwise ``None``.
    """
    if not tac_input or not tac_input.strip():
        return None
    try:
        split = split_bulletin(tac_input.strip(), product=product)
        parts = parse_ahl(split.meta.ahl)
        issued = issued_at_from_yygggg(parts.yygggg)
        return ca_msc_filename(parts, issued_at=issued)
    except (BulletinSplitError, TypeError, ValueError):
        return None


def apply_ca_eccc_collect_output(
    xml: str,
    *,
    semantic_canonical: str,
    exchange_output: bool,
    product: str,
    tac_input: str | None,
    bulletin_identifier: str | None = None,
    bulletin_context: str | None = None,
) -> str:
    """
    Wrap inner CA IWXXM in MSC COLLECT envelope when exchange output is requested.

    Parameters
    ----------
    xml :
        Inner product XML from convert.
    semantic_canonical :
        Resolved semantic profile registry key.
    exchange_output :
        Operator flag requesting MSC exchange packaging.
    product :
        API product enum.
    tac_input :
        Original TAC for AHL / filename derivation.
    bulletin_identifier :
        Precomputed MSC filename when already known (e.g. from ``output_spec``).
    bulletin_context :
        Optional full bulletin text when ``tac_input`` is a single report line.

    Returns
    -------
    str
        COLLECT-wrapped XML when requested and bulletin context exists; else ``xml``.
    """
    if semantic_canonical != "ca_eccc" or not exchange_output:
        return xml
    bulletin_id = bulletin_identifier or ca_collect_bulletin_identifier(
        product=product,
        tac_input=tac_input,
    )
    if not bulletin_id and bulletin_context:
        bulletin_id = ca_collect_bulletin_identifier(product=product, tac_input=bulletin_context)
    if not bulletin_id:
        return xml
    return wrap_ca_eccc_collect(xml, bulletin_identifier=bulletin_id)


__all__ = [
    "apply_ca_eccc_collect_output",
    "ca_collect_bulletin_identifier",
    "ca_eccc_output_spec_for_request",
]
