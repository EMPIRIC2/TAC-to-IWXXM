"""TC-EV-CMO-001..005 — CMO Week 1 evaluation corpus.

[Corpus: product §F6] [Corpus: product §F2] [Corpus: tests]
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from iwxxm_validate import validate
from tests.cmo_week1.matrix_lib import (
    Message,
    _disposition,
    load_corpus,
    parse_ahl_bulletin,
    parse_sigmet_file,
    run_matrix,
)

from tac2iwxxm import convert

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "tests" / "fixtures" / "cmo_week1"


def test_tc_ev_cmo_001_source_files_staged() -> None:
    """AC1: four Week 1 TAC sources + provenance README are staged."""
    for name in ("metar.txt", "speci.txt", "taf.txt", "sigmet.txt", "README.md"):
        path = FIXTURES / name
        assert path.is_file(), path
        assert path.stat().st_size > 0


def test_tc_ev_cmo_002_parser_message_counts() -> None:
    """AC2: parser yields the authoritative Week 1 message counts."""
    msgs = load_corpus()
    by: dict[str, int] = {}
    for m in msgs:
        by[m.dataset] = by.get(m.dataset, 0) + 1
    assert by["metar"] == 497
    assert by["speci"] == 42
    assert by["taf"] == 21
    assert by["sigmet"] == 19
    assert len(msgs) == 579


def test_tc_ev_cmo_003_smoke_convert_validate_per_product() -> None:
    """AC3: one Caribbean-shaped message per product converts and validates."""
    cases = [
        (
            "METAR",
            "METAR TTPP 081600Z 11015KT 7000 FEW022 32/23 Q1014 NOSIG",
        ),
        (
            "SPECI",
            "SPECI TTPP 080020Z 11003KT 7000 FEW015 28/22 Q1014 NOSIG=",
        ),
        (
            "TAF",
            "TAF MZBZ 081500Z 0818/0918 12008KT 9999 SCT024",
        ),
        (
            "SIGMET",
            "TTZP SIGMET 3 VALID 251435/251835 TTPP- TTZP PIARCO FIR EMBD TS OBS AT 1410Z "
            "WI N1800 W05406 - N1800 W05039 - N1031 W05542 - N1316 W05936 - N1800 W05406 "
            "TOP ABV FL380 STNR DECR=",
        ),
    ]
    for product, tac in cases:
        result = convert(tac, product=product, profile="annex3", iwxxm_version="2025-2")
        assert result.ok, (product, [i.code for i in result.issues])
        assert result.xml
        report = validate(result.xml, iwxxm_version="2025-2", profile="annex3")
        assert report.ok, (product, [i.code for i in report.issues])


def test_tc_ev_cmo_004_matrix_summary_artifact() -> None:
    """AC4: committed matrix summary reflects last full runner pass."""
    summary_path = FIXTURES / "matrix-summary.json"
    assert summary_path.is_file()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["total"] == 579
    assert summary["convert_ok"] == 579
    assert summary["validate_ok"] == 579
    assert summary["profile"] == "annex3"
    assert summary["iwxxm_version"] == "2025-2"
    # Disposition labels may still flag source quirks (typos/SIGA0/bare ICAO) for
    # evaluator notes; convert_ok is the harden gate.
    assert summary["message_counts"]["sigmet"] == 19
    assert summary["message_counts"]["speci"] == 42


def test_tc_ev_cmo_005_authoritative_oddities_preserved() -> None:
    """AC5: SPECI-set oddities remain in source (not cleaned)."""
    speci = (FIXTURES / "speci.txt").read_text(encoding="utf-8")
    assert "METAR TBPB 101500Z" in speci
    assert "MKJP 192303Z" in speci
    taf = (FIXTURES / "taf.txt").read_text(encoding="utf-8")
    assert "EMPO" in taf
    assert "TEMPO 0904/0910" in taf
    metar = (FIXTURES / "metar.txt").read_text(encoding="utf-8")
    assert "NOISG" in metar
    assert "VIS16KIM" in metar


@pytest.mark.parametrize(
    ("dataset", "path", "default"),
    [
        ("metar", "metar.txt", "METAR"),
        ("speci", "speci.txt", "SPECI"),
        ("taf", "taf.txt", "TAF"),
    ],
)
def test_ahl_parser_nonempty(dataset: str, path: str, default: str) -> None:
    text = (FIXTURES / path).read_text(encoding="utf-8")
    msgs = parse_ahl_bulletin(text, dataset=dataset, default_product=default)
    assert msgs
    assert all(m.tac.strip() for m in msgs)


def test_sigmet_parser_includes_siga0() -> None:
    text = (FIXTURES / "sigmet.txt").read_text(encoding="utf-8")
    msgs = parse_sigmet_file(text)
    siga = [m for m in msgs if m.tac.lstrip().startswith("SIGA0")]
    assert len(siga) == 2


def test_disposition_empo_not_tempo_false_positive() -> None:
    msg = Message(
        dataset="taf",
        index=0,
        ahl=None,
        tac="TAF TTPP 081600Z 0818/0918 10012KT 9999 SCT022 TEMPO 0900/0902 SHRA",
        product="TAF",
    )
    assert _disposition(msg, convert_ok=True, validate_ok=True) == "pass"
    msg2 = Message(
        dataset="taf",
        index=1,
        ahl=None,
        tac="TAF MWCR 081100Z 0812/0912 08009KT 9999 FEW018 PROB30 EMPO 0906/0909 TSRA",
        product="TAF",
    )
    assert (
        _disposition(msg2, convert_ok=True, validate_ok=True)
        == "authoritative_token_typo"
    )


def test_run_matrix_limit_writes_report(tmp_path: Path) -> None:
    report = run_matrix(evidence=tmp_path, limit=3)
    assert report["summary"]["total"] == 3
    assert (tmp_path / "matrix-report.json").is_file()
    # Must not clobber the committed full-corpus summary
    summary = json.loads((FIXTURES / "matrix-summary.json").read_text(encoding="utf-8"))
    assert summary["total"] == 579
