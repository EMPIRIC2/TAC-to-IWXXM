"""Shim-drop regressions for EV-packages-module-reorg L2.

[Corpus: product §F6] [Corpus: product §M1] [Corpus: tests]
"""

from __future__ import annotations

import importlib
import sys

import pytest


def test_annex3_products_module_removed() -> None:
    """Former pass-through path is gone after import retarget."""
    sys.modules.pop("tac2iwxxm.profiles.annex3_products", None)
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("tac2iwxxm.profiles.annex3_products")


def test_annex3_emit_exports_public_emitters() -> None:
    from tac2iwxxm.profiles.annex3_emit import (
        emit_airmet_annex3,
        emit_sigmet_annex3,
        emit_swxa_annex3,
        emit_taf_annex3,
        emit_tca_annex3,
        emit_vaa_annex3,
        emit_vona_annex3,
    )

    assert callable(emit_taf_annex3)
    assert callable(emit_sigmet_annex3)
    assert callable(emit_airmet_annex3)
    assert callable(emit_vaa_annex3)
    assert callable(emit_tca_annex3)
    assert callable(emit_swxa_annex3)
    assert callable(emit_vona_annex3)


def test_products_package_no_longer_reexports_parsers() -> None:
    import tac2iwxxm.products as products

    assert not hasattr(products, "parse_taf")
    assert not hasattr(products, "parse_metar_speci")
    assert not hasattr(products, "parse_sigmet")
    # fir_geometry remains a real submodule under products/
    from tac2iwxxm.products import fir_geometry

    assert fir_geometry is not None
