"""CA_ECCC profile stub — Canadian METAR/SPECI via ICAO baseline (#916 / EV-063 M8).

National ``iwxxm-ca`` extensions are not vendored yet; this module delegates METAR/SPECI
body encoding to annex3 until #916 lands vendor pins and MANOBS-specific RMK rules.

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: adr/ADR-036]
"""

from __future__ import annotations

from typing import Any

from tac2iwxxm.profiles.annex3 import emit_metar_speci_annex3


def emit_metar_speci_ca_eccc(
    ir: dict[str, Any],
    *,
    product: str,
    iwxxm_version: str,
) -> str:
    """
    Emit METAR/SPECI IWXXM for profile ``CA_ECCC`` (stub).

    Parameters
    ----------
    ir :
        Parsed intermediate representation from ``parse_metar_speci``.
    product :
        ``METAR`` or ``SPECI``.
    iwxxm_version :
        Target IWXXM release line.

    Returns
    -------
    str
        IWXXM XML using the annex3 encoder until Canadian extensions are pinned.
    """
    return emit_metar_speci_annex3(ir, product=product, iwxxm_version=iwxxm_version)


__all__ = ["emit_metar_speci_ca_eccc"]
