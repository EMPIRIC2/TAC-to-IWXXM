"""F29 / #831 quality-matrix helpers (EV-030).

Shared YAML/JSON RuleCase loaders for lint / convert / validate matrices.
Runners land in T1.2.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, cast

import yaml

Bucket = Literal["happy", "sad", "edge_pass", "edge_fail"]
Engine = Literal["lint", "convert", "validate"]
CaseStatus = Literal["ready", "needs-fixture", "oos"]

BUCKETS: tuple[Bucket, ...] = ("happy", "sad", "edge_pass", "edge_fail")
ENGINES: tuple[Engine, ...] = ("lint", "convert", "validate")
CASE_STATUSES: tuple[CaseStatus, ...] = ("ready", "needs-fixture", "oos")

_CASE_SUFFIXES: tuple[str, ...] = (".yml", ".yaml", ".json")


def _as_str_any_dict(value: object, *, path: Path, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{path}: {field_name} must be a mapping")
    out: dict[str, Any] = {}
    for key_obj, item in cast(dict[object, object], value).items():
        if not isinstance(key_obj, str):
            raise ValueError(f"{path}: {field_name} keys must be strings")
        out[key_obj] = item
    return out


def _load_mapping(path: Path) -> dict[str, object]:
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")
    if suffix in {".yml", ".yaml"}:
        raw_obj: object = yaml.safe_load(text)
    elif suffix == ".json":
        raw_obj = json.loads(text)
    else:
        raise ValueError(
            f"{path}: unsupported case file extension {suffix!r} "
            f"(expected {_CASE_SUFFIXES})"
        )
    if not isinstance(raw_obj, dict):
        raise ValueError(f"{path}: root must be a mapping")
    return cast(dict[str, object], raw_obj)


def _normalize_case_id(raw_case_id: object, *, path: Path, index: int) -> str:
    if isinstance(raw_case_id, int):
        case_id = f"{raw_case_id:02d}" if raw_case_id < 100 else str(raw_case_id)
    elif isinstance(raw_case_id, str):
        case_id = raw_case_id.strip()
    else:
        raise ValueError(f"{path}: cases[{index}] case_id must be str or int")
    if not (len(case_id) == 2 and case_id.isdigit()):
        raise ValueError(
            f"{path}: cases[{index}] case_id must be two digits (got {case_id!r})"
        )
    return case_id


def _meta_has_cite(meta: dict[str, Any]) -> bool:
    for key in ("cite", "reason", "oos_cite"):
        value = meta.get(key)
        if isinstance(value, str) and value.strip():
            return True
    return False


@dataclass(frozen=True)
class RuleCase:
    """One matrix slot: rule x bucket x case id."""

    rule_id: str
    engine: Engine
    bucket: Bucket
    case_id: str
    tac: str | None = None
    status: CaseStatus = "ready"
    expect: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def node_id(self) -> str:
        """Stable pytest / failure id: ``RULE/bucket/case``."""
        return f"{self.rule_id}/{self.bucket}/{self.case_id}"


def load_rule_cases(path: Path) -> list[RuleCase]:
    """Load RuleCase list from a YAML or JSON file.

    Accepted shapes:
    - ``{ rule_id, engine, cases: [ {bucket, case_id, ...}, ... ] }``
    - ``{ cases: [ {rule_id, engine, bucket, case_id, ...}, ... ] }``
    """
    raw = _load_mapping(path)

    cases_obj = raw.get("cases")
    if not isinstance(cases_obj, list) or not cases_obj:
        raise ValueError(f"{path}: 'cases' must be a non-empty list")
    cases_raw = cast(list[object], cases_obj)

    default_rule = raw.get("rule_id")
    default_engine = raw.get("engine")
    out: list[RuleCase] = []
    seen_node_ids: set[str] = set()

    for i, item_obj in enumerate(cases_raw):
        if not isinstance(item_obj, dict):
            raise ValueError(f"{path}: cases[{i}] must be a mapping")
        item = cast(dict[str, object], item_obj)
        rule_id = item.get("rule_id", default_rule)
        engine_obj = item.get("engine", default_engine)
        if not isinstance(rule_id, str) or not rule_id.strip():
            raise ValueError(f"{path}: cases[{i}] missing rule_id")
        if engine_obj not in ENGINES:
            raise ValueError(f"{path}: cases[{i}] invalid engine {engine_obj!r}")
        engine: Engine = engine_obj  # narrowed by membership check above
        bucket_obj = item.get("bucket")
        if bucket_obj not in BUCKETS:
            raise ValueError(f"{path}: cases[{i}] invalid bucket {bucket_obj!r}")
        bucket: Bucket = bucket_obj  # narrowed
        case_id = _normalize_case_id(item.get("case_id"), path=path, index=i)
        status_obj = item.get("status", "ready")
        if status_obj not in CASE_STATUSES:
            raise ValueError(f"{path}: cases[{i}] invalid status {status_obj!r}")
        status: CaseStatus = status_obj  # narrowed
        tac_obj = item.get("tac")
        if tac_obj is not None and not isinstance(tac_obj, str):
            raise ValueError(f"{path}: cases[{i}] tac must be string or null")
        tac: str | None = tac_obj
        expect = _as_str_any_dict(
            item.get("expect") or {}, path=path, field_name="expect"
        )
        meta = _as_str_any_dict(item.get("meta") or {}, path=path, field_name="meta")

        if status == "ready" and not (isinstance(tac, str) and tac.strip()):
            raise ValueError(f"{path}: cases[{i}] status ready requires non-empty tac")
        if status == "oos" and not _meta_has_cite(meta):
            raise ValueError(f"{path}: cases[{i}] status oos requires meta cite/reason")

        case = RuleCase(
            rule_id=rule_id.strip(),
            engine=engine,
            bucket=bucket,
            case_id=case_id,
            tac=tac,
            status=status,
            expect=expect,
            meta=meta,
        )
        if case.node_id in seen_node_ids:
            raise ValueError(f"{path}: duplicate node_id {case.node_id!r}")
        seen_node_ids.add(case.node_id)
        out.append(case)
    return out


def discover_rule_case_files(root: Path) -> list[Path]:
    """Discover ``.yml`` / ``.yaml`` / ``.json`` case files under ``root``.

    Intended layout (T0.1)::

        testdata/
          lint/<product>/<RULE>.yml
          convert/<product>/<ENCODE_ID>.json
          validate/<product>/<SCH_ID>.yml
    """
    if not root.is_dir():
        raise ValueError(f"{root}: expected a directory")
    found = [
        path
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.suffix.lower() in _CASE_SUFFIXES
    ]
    return found


def load_rule_cases_tree(root: Path) -> list[RuleCase]:
    """Load and concatenate all RuleCase files discovered under ``root``."""
    cases: list[RuleCase] = []
    for path in discover_rule_case_files(root):
        cases.extend(load_rule_cases(path))
    return cases
