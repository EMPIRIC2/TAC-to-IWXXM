"""Coverage for scripts/ci/populate_project_board_fields.py (EV-project-board-planning)."""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest
import scripts.ci.populate_project_board_fields as mod


def _proc(stdout: str = "", stderr: str = "", returncode: int = 0) -> SimpleNamespace:
    return SimpleNamespace(stdout=stdout, stderr=stderr, returncode=returncode)


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mod.time, "sleep", lambda *_a, **_k: None)


@pytest.mark.unit
def test_gql_success(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {"data": {"viewer": {"login": "x"}}}

    def fake_run(*_a: Any, **_k: Any) -> SimpleNamespace:
        return _proc(stdout=json.dumps(payload))

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    assert mod.gql("{ viewer { login } }") == {"viewer": {"login": "x"}}


@pytest.mark.unit
def test_gql_with_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, Any] = {}

    def fake_run(*_a: Any, **kwargs: Any) -> SimpleNamespace:
        seen["input"] = kwargs.get("input")
        return _proc(stdout=json.dumps({"data": {"ok": True}}))

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    assert mod.gql("query($c:String){x}", {"c": "cursor"}) == {"ok": True}
    assert '"c": "cursor"' in (seen["input"] or "")


@pytest.mark.unit
def test_gql_rate_limit_then_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {"n": 0}

    def fake_run(*_a: Any, **_k: Any) -> SimpleNamespace:
        calls["n"] += 1
        if calls["n"] == 1:
            return _proc(
                stdout=json.dumps(
                    {"errors": [{"message": "API rate limit already exceeded"}]}
                )
            )
        return _proc(stdout=json.dumps({"data": {"ok": 1}}))

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    assert mod.gql("q") == {"ok": 1}
    assert calls["n"] == 2


@pytest.mark.unit
def test_gql_non_rate_limit_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_a: Any, **_k: Any) -> SimpleNamespace:
        return _proc(stdout=json.dumps({"errors": [{"message": "boom"}]}))

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="boom"):
        mod.gql("q")


@pytest.mark.unit
def test_gql_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_a: Any, **_k: Any) -> SimpleNamespace:
        return _proc(stdout="not-json", stderr="")

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="not-json"):
        mod.gql("q")


@pytest.mark.unit
def test_gql_nonzero_returncode(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_a: Any, **_k: Any) -> SimpleNamespace:
        return _proc(stdout=json.dumps({"data": {"x": 1}}), returncode=1)

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError):
        mod.gql("q")


@pytest.mark.unit
def test_gql_rate_limit_exhausted(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_a: Any, **_k: Any) -> SimpleNamespace:
        return _proc(stdout=json.dumps({"errors": [{"message": "rate limit hit"}]}))

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="rate limit exhausted"):
        mod.gql("q")


def _iter_response() -> dict[str, Any]:
    opts = [
        {"id": f"opt-{name}", "name": name}
        for name in (
            "I00-Backlog",
            "I01",
            "I02",
            "I03",
            "I04",
            "I05",
            "I06",
            "I07",
            "I09",
            "I10",
            "I11",
            "I12",
            "I13",
            "I14",
            "I15",
            "I16",
            "I17",
            "I18",
            "I19",
            "I21",
            "I23",
            "I24",
            "I25",
        )
    ]
    return {
        "organization": {
            "projectV2": {"f": {"options": opts}},
        }
    }


def _items_pages(include_all: bool = True) -> list[dict[str, Any]]:
    nums = sorted(mod.PLAN) if include_all else sorted(mod.PLAN)[:-1]
    mid = max(1, len(nums) // 2)
    page1_nums, page2_nums = nums[:mid], nums[mid:]
    nodes1 = [
        {"id": f"item-{n}", "content": {"number": n, "state": "OPEN"}}
        for n in page1_nums
    ]
    nodes1.append({"id": "skip-closed", "content": {"number": 1, "state": "CLOSED"}})
    nodes1.append({"id": "skip-empty", "content": {}})
    nodes2 = [
        {"id": f"item-{n}", "content": {"number": n, "state": "OPEN"}}
        for n in page2_nums
    ]
    return [
        {
            "organization": {
                "projectV2": {
                    "items": {
                        "pageInfo": {"hasNextPage": True, "endCursor": "c1"},
                        "nodes": nodes1,
                    }
                }
            }
        },
        {
            "organization": {
                "projectV2": {
                    "items": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "nodes": nodes2,
                    }
                }
            }
        },
    ]


@pytest.mark.unit
def test_main_ok(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    pages = _items_pages(include_all=True)
    calls = {"items": 0}

    def fake_gql(query: str, variables: dict | None = None) -> dict[str, Any]:
        if (
            'field(name: "Iteration")' in query
            or 'field(name: "Iteration")' in query.replace("\n", "")
        ):
            return _iter_response()
        if "items(first:" in query.replace(" ", ""):
            idx = calls["items"]
            calls["items"] += 1
            return pages[idx]
        # mutations
        return {"updateProjectV2ItemFieldValue": {"projectV2Item": {"id": "x"}}}

    monkeypatch.setattr(mod, "gql", fake_gql)
    assert mod.main() == 0
    out = capsys.readouterr().out
    assert '"ok":' in out
    assert '"fail": 0' in out


@pytest.mark.unit
def test_main_missing_and_fail(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    pages = _items_pages(include_all=False)

    def fake_gql(query: str, variables: dict | None = None) -> dict[str, Any]:
        if "Iteration" in query and "options" in query:
            return _iter_response()
        if "items(first" in query:
            # single page with incomplete set
            nodes = pages[0]["organization"]["projectV2"]["items"]["nodes"]
            return {
                "organization": {
                    "projectV2": {
                        "items": {
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                            "nodes": nodes,
                        }
                    }
                }
            }
        raise RuntimeError("mutate fail")

    monkeypatch.setattr(mod, "gql", fake_gql)
    assert mod.main() == 1
    captured = capsys.readouterr()
    assert "MISSING" in captured.err or "FAIL" in captured.out


@pytest.mark.unit
def test_entry_raises_system_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mod, "main", lambda: 3)
    with pytest.raises(SystemExit) as exc:
        mod._entry()
    assert exc.value.code == 3


@pytest.mark.unit
def test_dunder_main_via_run_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Execute the real ``if __name__ == "__main__"`` guard without network."""
    import runpy
    from pathlib import Path

    pages = _items_pages(include_all=True)
    state = {"items": 0}

    def fake_run(*_a: object, **kwargs: object) -> SimpleNamespace:
        raw = str(kwargs.get("input") or "")
        if "Iteration" in raw and "options" in raw:
            body = {"data": _iter_response()}
        elif "items" in raw and "pageInfo" in raw:
            idx = state["items"]
            state["items"] += 1
            body = {"data": pages[min(idx, len(pages) - 1)]}
        else:
            body = {
                "data": {
                    "updateProjectV2ItemFieldValue": {"projectV2Item": {"id": "x"}}
                }
            }
        return _proc(stdout=json.dumps(body))

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    monkeypatch.setattr(mod.time, "sleep", lambda *_a, **_k: None)
    # Also patch the stdlib modules the fresh run_path import will bind.
    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr("time.sleep", lambda *_a, **_k: None)

    path = Path(mod.__file__).resolve()
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(path), run_name="__main__")
    assert exc.value.code == 0
