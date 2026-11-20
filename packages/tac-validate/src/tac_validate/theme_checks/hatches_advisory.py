"""Theme hatch wrappers."""

# ruff: noqa: F403, F405
# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

from tac_validate.theme_checks.themes import *


def hatch_vaa(tac_text: str, product: str) -> list[Issue]:
    """
    Detector hatch for VAA checklist.


    Parameters
    ----------
    tac_text : str
        TAC text.
    product : str
        Product id.

    Returns
    -------
    list[Issue]
        Detector hatch for VAA checklist.
    """
    del product
    from tac_validate.product_rules_pkg.vaa import _check_vaa

    return _check_vaa(tac_text)


def hatch_tca(tac_text: str, product: str) -> list[Issue]:
    """
    Detector hatch for TCA checklist.


    Parameters
    ----------
    tac_text : str
        TAC text.
    product : str
        Product id.

    Returns
    -------
    list[Issue]
        Detector hatch for TCA checklist.
    """
    del product
    from tac_validate.product_rules_pkg.tca import _check_tca

    return _check_tca(tac_text, profile=lint_profile.get())
