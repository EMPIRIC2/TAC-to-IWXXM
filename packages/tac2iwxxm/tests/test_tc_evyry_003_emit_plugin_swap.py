"""TC-EVYRY-003: emit-map plugin swap changes IWXXM (ADR-049 / #1256)."""

from __future__ import annotations

from pathlib import Path

import pytest
from tac2iwxxm.convert import convert
from tac2iwxxm.emit_map import ENV_EMIT_MAP_DIR, clear_emit_map_catalog_cache, emit_with_map

_FIXTURES = Path(__file__).resolve().parents[0] / "fixtures" / "annex3_golden"
_SENTINEL = "python:tac2iwxxm.emit_map:emit_plugin_sentinel"

# profile, product, builtin map id, fixture, pin
_CASES = [
    ("annex3", "METAR", "annex3-metar-speci-emit", "metar_basic.tac", "2025-2"),
    ("annex3", "TAF", "annex3-taf-emit", "taf_basic.tac", "2025-2"),
    ("annex3", "SIGMET", "annex3-sigmet-emit", "sigmet_a6_1a_ts.tac", "2025-2"),
    ("annex3", "AIRMET", "annex3-airmet-emit", "airmet_a6_1a_ts.tac", "2025-2"),
    ("annex3", "VAA", "annex3-vaa-emit", "vaa_a7_2.tac", "2025-2"),
    ("annex3", "TCA", "annex3-tca-emit", "tca_a2_2.tac", "2025-2"),
    ("iwxxm_us", "METAR", "iwxxm-us-metar-speci-emit", "metar_basic.tac", "2025-2"),
    ("ca_eccc", "METAR", "ca-eccc-metar-speci-emit", "metar_basic.tac", "3.0.0"),
]


@pytest.fixture(autouse=True)
def _clear_catalog() -> None:
    clear_emit_map_catalog_cache()
    yield
    clear_emit_map_catalog_cache()


@pytest.mark.parametrize(("profile", "product", "extends", "fixture", "pin"), _CASES)
def test_plugin_swap_changes_output(
    profile: str,
    product: str,
    extends: str,
    fixture: str,
    pin: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tac = (_FIXTURES / fixture).read_text(encoding="utf-8")
    monkeypatch.delenv(ENV_EMIT_MAP_DIR, raising=False)
    clear_emit_map_catalog_cache()
    baseline = convert(tac, product=product, profile=profile, iwxxm_version=pin)
    assert baseline.ok
    assert baseline.xml
    assert baseline.ir
    (tmp_path / "swap.yaml").write_text(
        "\n".join(
            [
                "schema_version: 1",
                f"id: {extends}-sentinel",
                f"extends: {extends}",
                "kind: python_plugin",
                f"plugin: {_SENTINEL}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv(ENV_EMIT_MAP_DIR, str(tmp_path))
    clear_emit_map_catalog_cache()
    swapped = emit_with_map(
        baseline.ir,
        product=product,
        profile=profile,
        iwxxm_version=pin,
    )
    assert swapped.startswith("sentinel:")
    assert swapped != baseline.xml
