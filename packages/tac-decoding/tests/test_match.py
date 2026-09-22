"""T1.2 — token-stream and label-field matchers. Version stays with the caller.

[Corpus: adr/ADR-045]
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tac_decoding.match import MatchBudgetError, MatchContext, match_tac
from tac_decoding.packs import PackSchemaError, load_packs


def _overlay(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, text: str) -> None:
    (tmp_path / "pack.yaml").write_text(text, encoding="utf-8")
    monkeypatch.setenv("TAC_DECODING_PACK_DIR", str(tmp_path))


def test_token_span_and_residual(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _overlay(
        monkeypatch,
        tmp_path,
        """
id: fixture_metar
layout: token_stream
rules:
  - id: skip
    pattern: ["ZZZ"]
    explain: "No {0}"
  - id: vis
    pattern: ["\\\\d+", "\\\\d+/\\\\d+SM"]
    explain: "Visibility {0} {1}"
""",
    )
    pack = {item.id: item for item in load_packs()}["fixture_metar"]
    result = match_tac("1 1/2SM KJFK=", pack, context=MatchContext("2025-2", "annex3"))
    assert result.spans[0].code == "1 1/2SM"
    assert result.spans[0].explanation == "Visibility 1 1/2SM"
    assert result.residuals[0].code == "KJFK"
    assert result.residuals[1].code == "="
    assert result.iwxxm_version == "2025-2"
    assert result.profile == "annex3"


def test_same_explain_on_every_pin(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _overlay(
        monkeypatch,
        tmp_path,
        """
id: fixture_metar
layout: token_stream
rules:
  - id: kind
    pattern: ["METAR"]
    explain: "Routine {0}"
""",
    )
    pack = {item.id: item for item in load_packs()}["fixture_metar"]
    pins = (
        MatchContext("2023-1", "annex3"),
        MatchContext("2025-2", "annex3"),
        MatchContext("3.0.0", "ca_eccc"),
        MatchContext("not-a-pin", "other"),
    )
    spans = [match_tac("METAR", pack, context=pin).spans for pin in pins]
    assert spans[0] == spans[1] == spans[2] == spans[3]
    bare = match_tac("METAR", pack)
    assert bare.spans == spans[0]
    assert bare.iwxxm_version is None


def test_label_longest_match(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _overlay(
        monkeypatch,
        tmp_path,
        """
id: fixture_vona
layout: label_fields
rules:
  - id: adv
    label: ADVISORY
    explain: "Advisory {value}"
  - id: nxt
    label: NXT ADVISORY
    explain: "Next {value}"
""",
    )
    pack = {item.id: item for item in load_packs()}["fixture_vona"]
    result = match_tac("NXT ADVISORY: 20260101\n\nplain\n", pack)
    assert result.spans[0].explanation == "Next 20260101"
    assert result.spans[0].rule_id == "nxt"
    assert result.residuals[0].code == "plain"


def test_stub_and_empty_rules_keep_legacy_path() -> None:
    packs = {item.id: item for item in load_packs()}
    stub = match_tac("WAFS body", packs["wafs"], context=MatchContext("3.0.0", "ca_eccc"))
    assert stub.spans == ()
    assert stub.residuals[0].code == "WAFS body"
    assert match_tac("", packs["wafs"]).residuals == ()
    # TAF builtin is filled this cycle (EV-pack-fill-delete-gate).
    filled = match_tac("TAF", packs["taf"])
    assert filled.residuals == ()
    assert filled.spans[0].code == "TAF"
    label = match_tac("VOLCANO: X\n", packs["vona"])
    assert label.spans
    assert label.spans[0].rule_id


def test_step_budget_fails_closed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _overlay(
        monkeypatch,
        tmp_path,
        """
id: fixture_metar
layout: token_stream
rules:
  - id: kind
    pattern: ["METAR"]
    explain: "{0}"
""",
    )
    pack = {item.id: item for item in load_packs()}["fixture_metar"]
    with pytest.raises(MatchBudgetError, match="0 steps"):
        match_tac("METAR", pack, max_steps=0)
    _overlay(
        monkeypatch,
        tmp_path,
        """
id: fixture_vona
layout: label_fields
rules:
  - id: vol
    label: VOLCANO
    explain: "Volcano {value}"
""",
    )
    label_pack = {item.id: item for item in load_packs()}["fixture_vona"]
    with pytest.raises(MatchBudgetError, match="0 steps"):
        match_tac("VOLCANO: X", label_pack, max_steps=0)


@pytest.mark.parametrize(
    ("text", "match"),
    [
        ("id: m\nlayout: token_stream\nrules: nope\n", "list"),
        (
            "id: wafs-bad\nprofiles: [annex3]\nextends: wafs\nlayout: stub\nrules:\n  - id: a\n    explain: x\n",
            "stub",
        ),
        ("id: m\nlayout: token_stream\nrules:\n  - nope\n", "mapping"),
        (
            "id: m\nlayout: token_stream\nrules:\n  - id: a\n    explain: x\n    extra: 1\n",
            "unknown field",
        ),
        ("id: m\nlayout: token_stream\nrules:\n  - explain: x\n", "string id"),
        (
            "id: m\nlayout: token_stream\nrules:\n  - id: a\n    pattern: ['A']\n    explain: '{0}'\n"
            "  - id: a\n    pattern: ['B']\n    explain: '{0}'\n",
            "duplicated",
        ),
        ("id: m\nlayout: token_stream\nrules:\n  - id: a\n    pattern: ['A']\n", "explain"),
        (
            "id: m\nlayout: token_stream\nrules:\n  - id: a\n    explain: x\n    label: METAR\n    pattern: ['A']\n",
            "cannot have a label",
        ),
        ("id: m\nlayout: token_stream\nrules:\n  - id: a\n    explain: '{0}'\n    pattern: []\n", "pattern"),
        (
            "id: m\nlayout: token_stream\nrules:\n  - id: a\n    explain: '{0}'\n    pattern: ['']\n",
            "strings",
        ),
        (
            "id: m\nlayout: token_stream\nrules:\n  - id: a\n    explain: '{0}'\n    pattern: ['[']\n",
            "invalid pattern",
        ),
        (
            "id: m\nlayout: token_stream\nrules:\n  - id: a\n    explain: '{value}'\n    pattern: ['A']\n",
            "template",
        ),
        (
            "id: m\nlayout: label_fields\nrules:\n  - id: a\n    explain: '{value}'\n    label: A\n    pattern: ['A']\n",
            "cannot have a pattern",
        ),
        ("id: m\nlayout: label_fields\nrules:\n  - id: a\n    explain: '{value}'\n", "needs a label"),
        (
            "id: m\nlayout: label_fields\nrules:\n  - id: a\n    label: A\n    explain: '{0}'\n",
            "template",
        ),
    ],
)
def test_rule_schema_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    text: str,
    match: str,
) -> None:
    _overlay(monkeypatch, tmp_path, text)
    with pytest.raises(PackSchemaError, match=match):
        load_packs()
