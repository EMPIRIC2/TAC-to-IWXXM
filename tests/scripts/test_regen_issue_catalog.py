"""EV-080 coverage fills for scripts/tac-validate/regen_issue_catalog.py."""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest
from tests.scripts.conftest import load_script

regen = load_script("tac-validate/regen_issue_catalog.py")


def test_load_provenance_missing_and_bad(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(regen, "PROVENANCE", tmp_path / "missing.json")
    assert regen._load_provenance() == {}

    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(regen, "PROVENANCE", bad)
    assert regen._load_provenance() == {}

    good = tmp_path / "good.json"
    good.write_text(
        json.dumps({"catalog_codes": [{"code": "X", "source_id": "WMO"}]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(regen, "PROVENANCE", good)
    assert regen._load_provenance()["X"]["source_id"] == "WMO"


def test_attribution_fields_branches(capsys: pytest.CaptureFixture[str]) -> None:
    empty = regen._attribution_fields(None)
    assert empty["source_attribution"] is None

    full = regen._attribution_fields(
        {
            "source_id": "ICAO",
            "source_url": "https://example.com",
            "status": "paywall",
            "note": "public note",
        }
    )
    assert "ICAO" in full["source_attribution"]
    assert "access:paywall" in full["source_attribution"]

    regen._attribution_fields({"note": "see ADR-028 for details"})
    assert "omitting provenance note" in capsys.readouterr().err


def test_load_rows_import_fallbacks(monkeypatch: pytest.MonkeyPatch) -> None:
    broken = types.ModuleType("tac_validate.issue_registry")
    monkeypatch.setitem(sys.modules, "tac_validate.issue_registry", broken)
    rows, source = regen._load_rows()
    assert rows == []
    assert "stub" in source


def test_load_rows_module_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in list(sys.modules):
        if key == "tac_validate" or key.startswith("tac_validate."):
            monkeypatch.delitem(sys.modules, key, raising=False)

    import builtins

    real_import = builtins.__import__

    def fake_import(name: str, *args: object, **kwargs: object):
        if name in {"tac_validate", "tac_validate.issue_registry"} or name.startswith(
            "tac_validate."
        ):
            raise ModuleNotFoundError(f"No module named {name!r}", name=name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    rows, source = regen._load_rows()
    assert rows == regen._stub_rows()
    assert "stub" in source


def test_load_rows_module_not_found_reraises(monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins

    real_import = builtins.__import__

    def fake_import(name: str, *args: object, **kwargs: object):
        if name == "tac_validate.issue_registry":
            raise ModuleNotFoundError("missing dependency", name="requests")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(ModuleNotFoundError, match="missing dependency"):
        regen._load_rows()


def test_stable_generated_non_string_prior(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    js = tmp_path / "catalog.json"
    rows = [{"code": "A"}]
    js.write_text(
        json.dumps({"source": "src", "issues": rows, "generated": 12345}),
        encoding="utf-8",
    )
    monkeypatch.setattr(regen, "CATALOG_JSON", js)
    assert regen._stable_generated(rows, "src") != 12345


def test_load_provenance_skips_bad_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prov = tmp_path / "prov.json"
    prov.write_text(
        json.dumps(
            {
                "catalog_codes": [
                    "bad",
                    {"code": None},
                    {"code": "OK", "source_id": "WMO"},
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(regen, "PROVENANCE", prov)
    loaded = regen._load_provenance()
    assert loaded == {"OK": {"code": "OK", "source_id": "WMO"}}


def test_stable_generated_preserves_prior_date(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    js = tmp_path / "catalog.json"
    js.write_text("{bad", encoding="utf-8")
    monkeypatch.setattr(regen, "CATALOG_JSON", js)
    assert regen._stable_generated([], "src") != ""

    rows = [{"code": "A"}]
    js.write_text(
        json.dumps({"source": "src", "issues": rows, "generated": "2020-05-01"}),
        encoding="utf-8",
    )
    assert regen._stable_generated(rows, "src") == "2020-05-01"


def test_stable_generated_invalid_prior(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    js = tmp_path / "catalog-bad.json"
    js.write_text("{bad", encoding="utf-8")
    monkeypatch.setattr(regen, "CATALOG_JSON", js)
    assert regen._stable_generated([], "other-src") != ""


def test_write_attribution_skips_rows_without_code(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    attr = tmp_path / "attr.json"
    monkeypatch.setattr(regen, "ATTRIBUTION_JSON", attr)
    monkeypatch.setattr(regen, "PROVENANCE", tmp_path / "missing-prov.json")
    regen._write_attribution_package([{"severity": "info"}], "2026-01-01")
    assert json.loads(attr.read_text(encoding="utf-8"))["codes"] == {}


def test_load_rows_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_issues = [
        SimpleNamespace(
            code="METAR001",
            severity="warning",
            message_template="msg",
            product="metar",
            tags=("t",),
        )
    ]

    class FakeRegistry:
        ISSUES = fake_issues

    monkeypatch.setitem(sys.modules, "tac_validate.issue_registry", FakeRegistry())
    monkeypatch.setattr(
        regen, "_load_provenance", lambda: {"METAR001": {"source_id": "WMO"}}
    )
    rows, source = regen._load_rows()
    assert rows[0]["code"] == "METAR001"
    assert "generated" in source or "registry" in source


def test_stable_generated_and_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    md = tmp_path / "ISSUE_CATALOG.md"
    js = tmp_path / "ISSUE_CATALOG.json"
    attr = tmp_path / "catalog_attribution.json"
    monkeypatch.setattr(regen, "CATALOG_MD", md)
    monkeypatch.setattr(regen, "CATALOG_JSON", js)
    monkeypatch.setattr(regen, "ATTRIBUTION_JSON", attr)
    monkeypatch.setattr(regen, "PROVENANCE", tmp_path / "prov.json")

    rows = [
        {
            "code": "A",
            "severity": "info",
            "message_template": "m",
            "product": "metar",
            "tags": [],
        }
    ]
    source = "test-source"
    js.write_text(
        json.dumps({"source": source, "issues": rows, "generated": "2020-01-01"}),
        encoding="utf-8",
    )
    assert regen._stable_generated(rows, source) == "2020-01-01"
    assert regen._stable_generated(rows, "other") != "2020-01-01"

    regen._write_md([], source, "2026-01-01")
    assert "_(none yet)_" in md.read_text(encoding="utf-8")

    row = {
        "code": "B",
        "severity": "error",
        "message_template": "bad|pipe",
        "product": "metar",
        "tags": ["x"],
        "source_attribution": "cite|me",
    }
    regen._write_md([row], source, "2026-01-01")
    assert "\\|" in md.read_text(encoding="utf-8")

    regen._write_json([row], source, "2026-01-01")
    assert json.loads(js.read_text(encoding="utf-8"))["issues"][0]["code"] == "B"

    (tmp_path / "prov.json").write_text(
        json.dumps({"catalog_codes": [{"code": "B", "source_id": "WMO", "note": "n"}]}),
        encoding="utf-8",
    )
    regen._write_attribution_package([row], "2026-01-01")
    attr_data = json.loads(attr.read_text(encoding="utf-8"))
    assert attr_data["codes"]["B"]["source_id"] == "WMO"


def test_main(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(regen, "REPO", tmp_path)
    monkeypatch.setattr(regen, "CATALOG_MD", tmp_path / "ISSUE_CATALOG.md")
    monkeypatch.setattr(regen, "CATALOG_JSON", tmp_path / "ISSUE_CATALOG.json")
    monkeypatch.setattr(regen, "ATTRIBUTION_JSON", tmp_path / "attr.json")
    monkeypatch.setattr(regen, "_load_rows", lambda: ([], "stub source"))
    assert regen.main() == 0
    assert "Wrote" in capsys.readouterr().out
