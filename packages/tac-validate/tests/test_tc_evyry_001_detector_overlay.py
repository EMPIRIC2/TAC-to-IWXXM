"""TC-EVYRY-001: a detector overlay can replace a python hatch (ADR-049 / #1254)."""

from __future__ import annotations

from pathlib import Path

import pytest
from tac_validate.detectors import ENV_DETECTOR_DIR, load_detector_catalog, run_detector_pack

_TAC = "METAR KJFK 121255Z 10SM="
_OVERLAY = """
schema_version: 1
id: metar-speci-r3-weather-overlay
extends: metar-speci-r3-weather
profiles: [annex3]
stage: token
products: [METAR, SPECI]
rules:
  - id: r3_python
    kind: finditer
    pattern: '\\bMETAR\\b'
    on_match:
      code: COR_PRESENT
      location: modifier
      message_template: "{product} overlay replaced the weather hatch"
      span: match
"""


def test_overlay_replaces_r3_python_hatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ENV_DETECTOR_DIR, raising=False)
    builtin = load_detector_catalog(profile="annex3")["metar-speci-r3-weather"]
    before = {issue.code for issue in run_detector_pack(builtin, _TAC, "METAR")}
    assert builtin.rules[0].kind == "python"
    (tmp_path / "r3.yaml").write_text(_OVERLAY, encoding="utf-8")
    monkeypatch.setenv(ENV_DETECTOR_DIR, str(tmp_path))
    layered = load_detector_catalog(profile="annex3")["metar-speci-r3-weather"]
    after = {issue.code for issue in run_detector_pack(layered, _TAC, "METAR")}
    assert layered.rules[0].kind == "finditer"
    assert "COR_PRESENT" in after
    assert after != before
