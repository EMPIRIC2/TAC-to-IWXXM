"""T1.4 — English locale hook and sandboxed templates.

[Corpus: adr/ADR-045]
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tac_decoding.locale import ExplanationHook, LocaleError, render_template
from tac_decoding.match import match_tac
from tac_decoding.packs import PackSchemaError, load_packs


def _overlay(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, text: str) -> None:
    (tmp_path / "pack.yaml").write_text(text, encoding="utf-8")
    monkeypatch.setenv("TAC_DECODING_PACK_DIR", str(tmp_path))


_METAR = """
id: metar
layout: token_stream
rules:
  - id: kind
    pattern: ["METAR"]
    explain: "Routine {0}"
"""


def test_english_hook_replaces_one_phrase(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _overlay(monkeypatch, tmp_path, _METAR)
    pack = {item.id: item for item in load_packs()}["metar"]
    hook = ExplanationHook({"kind": "Report {0}"})
    result = match_tac("METAR", pack, hook=hook)
    assert result.spans[0].explanation == "Report METAR"
    kept = match_tac("METAR", pack, hook=ExplanationHook({"other": "nope"}))
    assert kept.spans[0].explanation == "Routine METAR"


def test_other_locale_fails_closed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _overlay(monkeypatch, tmp_path, _METAR)
    pack = {item.id: item for item in load_packs()}["metar"]
    with pytest.raises(LocaleError, match="not available"):
        match_tac("METAR", pack, locale="fr")
    with pytest.raises(LocaleError, match="not available"):
        render_template("Routine {0}", ("METAR",), locale="fr")


def test_sandbox_rejects_object_access() -> None:
    with pytest.raises(LocaleError, match="placeholder"):
        render_template("{0.__class__}", ("METAR",))
    with pytest.raises(LocaleError, match="format"):
        render_template("{0:>10}", ("METAR",))
    with pytest.raises(LocaleError, match="conversion"):
        render_template("{0!r}", ("METAR",))
    with pytest.raises(LocaleError, match="not allowed"):
        render_template("{", ("METAR",))


def test_unsafe_pack_template_fails_at_load(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _overlay(
        monkeypatch,
        tmp_path,
        """
id: metar
layout: token_stream
rules:
  - id: kind
    pattern: ["METAR"]
    explain: "{0.__class__}"
""",
    )
    with pytest.raises(PackSchemaError, match="template"):
        load_packs()
    _overlay(
        monkeypatch,
        tmp_path,
        "id: metar\nlayout: token_stream\nrules:\n  - id: kind\n    pattern: ['"
        + ("A" * 201)
        + "']\n    explain: '{0}'\n",
    )
    with pytest.raises(PackSchemaError, match="too long"):
        load_packs()
