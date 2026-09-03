"""Coverage fill for loader / execute edge branches."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from workflows.execute import WorkflowExecuteError
from workflows.loader import (
    WorkflowLoadError,
    assert_no_embedded_credentials,
    default_workflows_dir,
    load_workflow,
    parse_workflow_mapping,
    resolve_env_refs,
)
from workflows.stages import run_validate_schematron, run_validate_xsd

from workflows import WorkflowDefinition, WorkflowMessage, execute
from workflows import stages as stages_mod

pytestmark = pytest.mark.unit


def test_default_workflows_dir_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("WORKFLOWS_DIR", str(tmp_path))
    assert default_workflows_dir() == tmp_path


def test_resolve_env_list() -> None:
    assert resolve_env_refs(["${ENV:NOPE}", 1], environ={}) == ["", 1]


def test_credentials_in_list() -> None:
    with pytest.raises(WorkflowLoadError, match="credentials"):
        assert_no_embedded_credentials(["https://u:p@host/x"])


def test_parse_bad_version_and_profile() -> None:
    with pytest.raises(WorkflowLoadError, match="version"):
        parse_workflow_mapping({"id": "x", "version": 1, "pipeline": ["validate-tac"]})
    with pytest.raises(WorkflowLoadError, match="profile"):
        parse_workflow_mapping({"id": "x", "version": "1", "pipeline": ["validate-tac"], "profile": []})
    with pytest.raises(WorkflowLoadError, match="pipeline entries"):
        parse_workflow_mapping({"id": "x", "version": "1", "pipeline": [""]})
    with pytest.raises(WorkflowLoadError, match="pipeline entries"):
        parse_workflow_mapping({"id": "x", "version": "1", "pipeline": [1]})  # type: ignore[list-item]
    with pytest.raises(WorkflowLoadError, match="id is required"):
        parse_workflow_mapping({"id": "  ", "version": "1", "pipeline": ["validate-tac"]})
    with pytest.raises(WorkflowLoadError, match="id is required"):
        parse_workflow_mapping({"version": "1", "pipeline": ["validate-tac"]})


def test_profile_none_ok() -> None:
    d = parse_workflow_mapping({"id": "x", "version": "1", "pipeline": ["validate-tac"], "profile": None})
    assert d.profile_id == "annex3"


def test_default_workflows_dir_cwd_fallback(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("WORKFLOWS_DIR", raising=False)
    monkeypatch.setattr(
        "workflows.loader._find_workflows_dir",
        lambda _start: None,
    )
    monkeypatch.chdir(tmp_path)
    assert default_workflows_dir() == tmp_path / "workflows"


def test_load_resolve_non_mapping(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "x.yaml").write_text("id: x\npipeline: [validate-tac]\n", encoding="utf-8")
    monkeypatch.setattr(
        "workflows.loader.resolve_env_refs",
        lambda *_a, **_k: ["not-a-mapping"],
    )
    with pytest.raises(WorkflowLoadError, match="after resolve"):
        load_workflow("x", workflows_dir=tmp_path)


def test_sink_entry_dict_without_sink() -> None:
    d = parse_workflow_mapping(
        {
            "id": "x",
            "version": "1",
            "pipeline": ["validate-tac"],
            "onValid": {"store": [{"other": 1}]},
        }
    )
    assert d.on_valid_store == []


def test_sink_ids_string_and_bad_store() -> None:
    d = parse_workflow_mapping(
        {
            "id": "x",
            "version": "1",
            "pipeline": ["validate-tac"],
            "onValid": {"store": ["plain-sink"]},
            "onInvalid": {"store": "not-a-list"},
        }
    )
    assert d.on_valid_store == ["plain-sink"]
    assert d.on_invalid_store == []


def test_invalid_yaml(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text(": : :\n", encoding="utf-8")
    with pytest.raises(WorkflowLoadError, match="invalid YAML"):
        load_workflow("bad", workflows_dir=tmp_path)


def test_non_mapping_root(tmp_path: Path) -> None:
    (tmp_path / "list.yaml").write_text("- a\n", encoding="utf-8")
    with pytest.raises(WorkflowLoadError, match="mapping"):
        load_workflow("list", workflows_dir=tmp_path)


def test_execute_missing_workflow_id() -> None:
    with pytest.raises(WorkflowExecuteError, match="not found"):
        execute(
            WorkflowMessage(tac="x", product="METAR"),
            "does-not-exist-workflow",
            workflows_dir=Path("/tmp"),
        )


def test_store_invalid_port(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        stages_mod,
        "tac_lint_fn",
        lambda *_a, **_k: SimpleNamespace(
            ok=False,
            issues=[SimpleNamespace(severity="error", code="E", message="e")],
        ),
    )
    seen: list[str] = []

    def store_invalid(_r: Any, *, sink: str) -> None:
        seen.append(sink)

    definition = WorkflowDefinition(
        id="u",
        version="1",
        pipeline=["validate-tac"],
        on_invalid_store=["quarantine-db"],
    )
    result = execute(
        WorkflowMessage(tac="x", product="METAR"),
        definition,
        store_invalid=store_invalid,
    )
    assert result.ok is False
    assert seen == ["quarantine-db"]


def test_missing_xml_xsd_schematron() -> None:
    definition = WorkflowDefinition(id="u", version="1", pipeline=["validate-xsd"])
    msg = WorkflowMessage(tac="x", product="METAR")
    xsd = run_validate_xsd(msg, definition, xml=None)
    assert xsd.ok is False
    assert xsd.issues[0].code == "MISSING_XML"
    sch = run_validate_schematron(msg, definition, xml=None)
    assert sch.ok is False
    assert sch.issues[0].code == "MISSING_XML"


def test_find_workflows_dir_none(tmp_path: Path) -> None:
    from workflows.loader import _find_workflows_dir

    assert _find_workflows_dir(tmp_path / "nested" / "file.py") is None


def test_xsd_blocking_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        stages_mod,
        "tac_lint_fn",
        lambda *_a, **_k: SimpleNamespace(ok=True, issues=[]),
    )
    monkeypatch.setattr(
        stages_mod,
        "tac2iwxxm_convert_fn",
        lambda *_a, **_k: SimpleNamespace(ok=True, xml="<x/>", issues=[]),
    )

    def _validate(*_a: Any, **kwargs: Any) -> Any:
        levels = kwargs.get("levels") or ()
        if "xsd" in levels:
            return SimpleNamespace(
                ok=False,
                issues=[
                    SimpleNamespace(severity="error", code="XSD_ERROR", message="bad"),
                ],
            )
        return SimpleNamespace(ok=True, issues=[])

    monkeypatch.setattr(stages_mod, "iwxxm_validate_fn", _validate)
    result = execute(
        WorkflowMessage(tac="METAR KJFK 231751Z NIL=", product="METAR"),
        WorkflowDefinition(
            id="u",
            version="1",
            pipeline=["validate-tac", "convert-iwxxm", "validate-xsd", "validate-schematron"],
        ),
    )
    assert result.ok is False
    assert result.stage_failed == "validate-xsd"
