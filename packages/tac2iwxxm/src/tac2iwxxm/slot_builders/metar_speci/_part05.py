"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def _product_matches_rtype(product: str, rtype: str) -> bool:
    """
    Internal helper ``_product_matches_rtype``.

    Parameters
    ----------
    product : str
        Argument ``product``.

    rtype : str
        Argument ``rtype``.

    Returns
    -------
    bool
        Return value.
    """
    product_u = product.upper()
    rtype_u = rtype.upper()
    if product_u == rtype_u:
        return True
    # CA_ECCC: API product METAR/SPECI accepts MANOBS LWIS/SAWR TAC leads (#1039).
    return bool(product_u in {"METAR", "SPECI"} and rtype_u in {"LWIS", "SAWR"})
