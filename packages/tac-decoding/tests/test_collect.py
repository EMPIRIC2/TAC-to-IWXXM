"""T5.1 — bulletin port and COLLECT reader (contained TAC or XML walk).

Bulletin split stays injected. COLLECT decodes contained TAC when present,
otherwise walks XML fields. No IWXXM encoder and no ``tac2iwxxm`` import.
[Corpus: tests] [Corpus: adr/ADR-045] [Corpus: system-spec]
"""

from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest
from tac_decoding.decode import decode_tac, set_bulletin_splitter

_REPO = Path(__file__).resolve().parents[3]
_CA_COLLECT = (
    _REPO
    / "packages"
    / "tac2iwxxm"
    / "tests"
    / "fixtures"
    / "profiles"
    / "CA_ECCC"
    / "METAR"
    / "ops"
    / "metar_basic_ops.xml"
)
_VENDOR_FAILED = (
    _REPO / "vendor" / "schemas" / "iwxxm" / "2025-2" / "IWXXM" / "examples" / "metar-translation-failed.xml"
)

_COLLECT_WITH_TAC = """\
<?xml version="1.0" encoding="UTF-8"?>
<collect:MeteorologicalBulletin xmlns:collect="http://def.wmo.int/collect/2014"
    xmlns:iwxxm="http://icao.int/iwxxm/2025-2"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    gml:id="uuid.collect.tac">
  <collect:meteorologicalInformation>
    <iwxxm:METAR gml:id="uuid.metar.1" reportStatus="NORMAL" permissibleUsage="OPERATIONAL"
        translationFailedTAC="METAR YUDO 221630Z 24004MPS 0600 DZ FG SCT010 OVC020 17/16 Q1018=">
      <iwxxm:issueTime>
        <gml:TimeInstant gml:id="uuid.t1">
          <gml:timePosition>2012-08-22T16:30:00Z</gml:timePosition>
        </gml:TimeInstant>
      </iwxxm:issueTime>
    </iwxxm:METAR>
  </collect:meteorologicalInformation>
  <collect:bulletinIdentifier>A_LAXX31YUDO221630_C_YUDO_20120822163000.xml</collect:bulletinIdentifier>
</collect:MeteorologicalBulletin>
"""


def test_bulletin_port_unset_does_not_split() -> None:
    from tac_decoding import decode as decode_mod

    ahl = "SAXX99 YUDO 121200\nMETAR YUDO 121200Z 00000KT CAVOK 10/10 Q1000=\n"
    previous = decode_mod._bulletin_splitter
    try:
        set_bulletin_splitter(None)
        result = decode_tac(ahl, product="METAR")
        assert "Bulletin" not in result.summary
    finally:
        set_bulletin_splitter(previous)


def test_bulletin_port_injected_splits_without_tac2iwxxm() -> None:
    from tac_decoding import decode as decode_mod

    ahl = "SAXX99 YUDO 121200\nMETAR YUDO 121200Z 00000KT CAVOK 10/10 Q1000=\n"
    report = "METAR YUDO 121200Z 00000KT CAVOK 10/10 Q1000="
    previous = decode_mod._bulletin_splitter

    def _fake_split(text: str, product: str) -> object:
        assert product == "METAR"
        assert "SAXX99" in text
        return SimpleNamespace(
            reports=[report],
            meta=SimpleNamespace(ahl="SAXX99 YUDO 121200", report_count=1),
        )

    try:
        set_bulletin_splitter(_fake_split)
        result = decode_tac(ahl, product="METAR")
        assert result.summary.startswith("Bulletin SAXX99 YUDO 121200")
        assert any(seg.code == "METAR" for seg in result.segments)
    finally:
        set_bulletin_splitter(previous)


def test_collect_with_contained_tac_decodes_the_report() -> None:
    from tac_decoding.collect import decode_collect, read_collect

    read = read_collect(_COLLECT_WITH_TAC)
    assert read.mode == "tac"
    assert read.bulletin_identifier == "A_LAXX31YUDO221630_C_YUDO_20120822163000.xml"
    assert len(read.tac_reports) == 1
    assert read.tac_reports[0].startswith("METAR YUDO")
    assert read.fields == ()

    result = decode_collect(_COLLECT_WITH_TAC, product="METAR")
    assert result.product == "METAR"
    assert "COLLECT" in result.summary
    assert any(seg.code == "METAR" for seg in result.segments)
    assert any("YUDO" in seg.code for seg in result.segments)


def test_vendor_translation_failed_is_contained_tac() -> None:
    from tac_decoding.collect import is_collect_input, read_collect

    xml = _VENDOR_FAILED.read_text(encoding="utf-8")
    assert is_collect_input(xml) is True
    read = read_collect(xml)
    assert read.mode == "tac"
    assert read.tac_reports == ("METAR YUDO 221630Z INVALID",)
    assert read.bulletin_identifier is None


def test_bare_iwxxm_without_failed_tac_is_collect_input() -> None:
    from tac_decoding.collect import is_collect_input

    xml = '<?xml version="1.0"?>\n<iwxxm:TAF xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>\n'
    assert is_collect_input(xml) is True


def test_collect_xml_only_walks_fields() -> None:
    from tac_decoding.collect import decode_collect, read_collect

    # Wrap the CA ops METAR (no translationFailedTAC) in a COLLECT shell.
    inner = _CA_COLLECT.read_text(encoding="utf-8")
    # Strip XML declaration from the inner document before nesting.
    body = inner.split("?>", 1)[-1].strip() if "?>" in inner else inner.strip()
    collect_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<collect:MeteorologicalBulletin xmlns:collect="http://def.wmo.int/collect/2014" '
        'xmlns:gml="http://www.opengis.net/gml/3.2" gml:id="uuid.ops">\n'
        f"  <collect:meteorologicalInformation>\n{body}\n  </collect:meteorologicalInformation>\n"
        "  <collect:bulletinIdentifier>A_TEST.xml</collect:bulletinIdentifier>\n"
        "</collect:MeteorologicalBulletin>\n"
    )
    read = read_collect(collect_xml)
    assert read.mode == "xml_walk"
    assert read.tac_reports == ()
    assert read.bulletin_identifier == "A_TEST.xml"
    names = {field.name for field in read.fields}
    assert "airTemperature" in names
    assert "designator" in names
    assert "timePosition" in names

    result = decode_collect(collect_xml, product="METAR")
    assert result.product == "METAR"
    assert "COLLECT" in result.summary
    assert any(seg.code == "airTemperature" for seg in result.segments)
    assert any("22.0" in seg.explanation for seg in result.segments)
    assert result.residuals == []


def test_collect_reader_does_not_encode_iwxxm() -> None:
    import tac_decoding
    from tac_decoding import collect as collect_mod

    root = Path(tac_decoding.__file__).resolve().parent
    text = Path(collect_mod.__file__).read_text(encoding="utf-8")
    for token in ("etree.tostring", "ElementTree.tostring"):
        assert token not in text, token
    offenders: list[str] = []
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
            for name in modules:
                top = name.split(".")[0]
                if top in {"tac2iwxxm", "lxml"}:
                    offenders.append(f"{path.name}:{name}")
    assert offenders == []


def test_decode_tac_dispatches_collect_xml() -> None:
    result = decode_tac(_COLLECT_WITH_TAC, product="METAR")
    assert "COLLECT" in result.summary
    assert any(seg.code == "METAR" for seg in result.segments)


def test_invalid_xml_is_not_collect() -> None:
    from tac_decoding.collect import CollectError, is_collect_input, read_collect

    assert is_collect_input("not xml") is False
    assert is_collect_input("<not closed") is False
    with pytest.raises(CollectError):
        read_collect("<not closed")
    with pytest.raises(CollectError, match="not a COLLECT"):
        read_collect("<note>hello</note>")


def test_entity_encoded_tac_still_decodes() -> None:
    from tac_decoding.collect import decode_collect

    xml = (
        '<?xml version="1.0"?>\n'
        '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2" '
        'translationFailedTAC="&#77;ETAR YUDO 221630Z 00000KT CAVOK 10/10 Q1000="/>\n'
    )
    result = decode_collect(xml, product="METAR")
    assert "COLLECT" in result.summary
    assert any(seg.code == "METAR" for seg in result.segments)


def test_entity_encoded_field_walk_offsets() -> None:
    from tac_decoding.collect import decode_collect, read_collect

    xml = (
        '<?xml version="1.0"?>\n'
        '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2" '
        'xmlns:aixm="http://www.aixm.aero/schema/5.1.1">\n'
        "  <aixm:designator>&#67;YUL</aixm:designator>\n"
        "</iwxxm:METAR>\n"
    )
    read = read_collect(xml)
    assert read.mode == "xml_walk"
    assert read.fields[0].value == "CYUL"
    result = decode_collect(xml, product="METAR")
    assert result.segments[0].code == "designator"
    assert result.segments[0].start == 0
    assert result.segments[0].end == 0


def test_xml_walk_truncates_long_summary() -> None:
    from tac_decoding.collect import decode_collect

    leaves = "\n".join(f"  <f{i}>{i}</f{i}>" for i in range(9))
    xml = f'<?xml version="1.0"?>\n<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2">\n{leaves}\n</iwxxm:METAR>\n'
    result = decode_collect(xml, product="METAR")
    assert len(result.segments) == 9
    assert result.summary.endswith("…")


def test_empty_iwxxm_walk_has_zero_fields() -> None:
    from tac_decoding.collect import decode_collect, read_collect

    xml = '<?xml version="1.0"?>\n<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>\n'
    assert read_collect(xml).fields == ()
    result = decode_collect(xml, product="METAR")
    assert result.segments == []
    assert "0 fields" in result.summary


def test_duplicate_contained_tac_reuses_source_offset() -> None:
    from tac_decoding.collect import decode_collect

    tac = "METAR YUDO 221630Z 00000KT CAVOK 10/10 Q1000="
    xml = (
        '<?xml version="1.0"?>\n'
        f'<wrapper><a translationFailedTAC="{tac}"/><b translationFailedTAC="{tac}"/></wrapper>\n'
    )
    result = decode_collect(xml, product="METAR")
    assert "2 report" in result.summary


def test_empty_inner_summary_is_skipped(monkeypatch: pytest.MonkeyPatch) -> None:
    from tac_decoding.collect import decode_collect
    from tac_decoding.decode import DecodeResult

    xml = (
        '<?xml version="1.0"?>\n'
        '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2" '
        'translationFailedTAC="METAR YUDO 221630Z INVALID"/>\n'
    )

    def _empty(_tac: str, *, product: str) -> DecodeResult:
        return DecodeResult(product=product, segments=[], residuals=[], summary="")

    monkeypatch.setattr("tac_decoding.decode.decode_single_report", _empty)
    result = decode_collect(xml, product="METAR")
    assert result.summary.startswith("COLLECT")
    assert "1 report" in result.summary


def test_failed_tac_on_non_iwxxm_wrapper() -> None:
    from tac_decoding.collect import is_collect_input, read_collect

    xml = '<wrapper translationFailedTAC="METAR YUDO 221630Z INVALID"/>'
    assert is_collect_input(xml) is True
    read = read_collect(xml)
    assert read.mode == "tac"
    assert read.tac_reports == ("METAR YUDO 221630Z INVALID",)
