"""TC-EV023-009 - Optional #798 QA deferral + matrix confirm (S030 / EV-023 T6.4).

Asserts coverage-matrix / theme-map citations stay wired and that defer-to-latest
METCE surfaces already shipped under S027 remain present on annex3 goldens.
Optional aviation-nil ``missing`` stubs beyond existing convert paths stay deferred
(see ``docs/sessions/S030-apac-encode-validate/reports/t6.4-optional-798-qa-matrix.md``).
"""

from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_MATRIX = _REPO / "docs" / "domain" / "rules" / "COVERAGE_MATRIX.md"
_THEME = _REPO / "docs" / "sessions" / "S030-apac-encode-validate" / "reports" / "apac-encode-theme-fixture-map.md"
_T64 = _REPO / "docs" / "sessions" / "S030-apac-encode-validate" / "reports" / "t6.4-optional-798-qa-matrix.md"
_GOLDEN = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"


def test_tc_ev023_009_matrix_and_theme_map_cite_s030() -> None:
    matrix = _MATRIX.read_text(encoding="utf-8")
    assert "#800" in matrix
    assert "S030-apac-encode-validate" in matrix
    assert "dissemination.collect_namespaces" in matrix
    assert _THEME.is_file()
    theme = _THEME.read_text(encoding="utf-8")
    assert "TC-EV023-009" in theme
    assert _T64.is_file()
    report = _T64.read_text(encoding="utf-8")
    assert "deferred" in report.lower()
    assert ".local/" in report


def test_tc_ev023_009_no_local_binaries_tracked() -> None:
    """Guard: `.local/` reference digests must not enter git (E23 / #798 OOS)."""
    import subprocess

    tracked = subprocess.check_output(
        ["git", "-C", str(_REPO), "ls-files", ".local", ".local/**"],
        text=True,
    ).strip()
    assert tracked == ""


def test_tc_ev023_009_metce_surfaces_survive_defer_to_latest() -> None:
    """S027 goldens already encode METCE cyclone / erupting volcano - not a new #798 gap."""
    tca = (_GOLDEN / "tca_a2_2.golden.xml").read_text(encoding="utf-8")
    vaa = (_GOLDEN / "vaa_a7_2.golden.xml").read_text(encoding="utf-8")
    assert "metce:TropicalCyclone" in tca
    assert "metce:EruptingVolcano" in vaa
