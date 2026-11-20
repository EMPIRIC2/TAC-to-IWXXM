"""Schema and intake integrity for docs/requirements.csv (CMO feedback).

[Corpus: product] [Corpus: tests]
Test matrix: Success / Failure / Validation pass+fail.
Mutation create/update/delete is N/A: cite-only CSV corpus, not a mutation API.
"""

from __future__ import annotations

import csv
import io
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
REQUIREMENTS = DOCS / "requirements.csv"

HEADER = (
    "id,source,priority,product_area,requirement,"
    "acceptance_criteria,status,notes"
)
ID_PATTERN = re.compile(r"^REQ-CMO-\d{3}$")
REQUIRED_NONEMPTY = (
    "id",
    "source",
    "priority",
    "product_area",
    "requirement",
    "acceptance_criteria",
    "status",
)
ALLOWED_PRIORITY = frozenset({"high", "med", "low"})
ALLOWED_STATUS = frozenset({"open", "mapped", "closed"})
ALLOWED_AREA = frozenset(
    {
        "convert",
        "validate",
        "accuracy",
        "usability",
        "error_handling",
        "performance",
        "testing",
        "adoption",
        "intake",
    }
)


def _read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    text = path.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text))
    assert reader.fieldnames is not None
    return list(reader.fieldnames), list(reader)


def _assert_schema(path: Path) -> list[dict[str, str]]:
    header_line = path.read_text(encoding="utf-8").splitlines()[0]
    assert header_line == HEADER, f"{path.name}: header drift"
    _, rows = _read_rows(path)
    assert rows, f"{path.name}: expected at least one data row"
    for row in rows:
        for key in REQUIRED_NONEMPTY:
            assert row.get(key, "").strip(), f"{path.name}: empty {key}"
        assert ID_PATTERN.match(row["id"]), f"{path.name}: bad id {row['id']!r}"
        assert row["priority"] in ALLOWED_PRIORITY, row["priority"]
        assert row["status"] in ALLOWED_STATUS, row["status"]
        assert row["product_area"] in ALLOWED_AREA, row["product_area"]
        assert row["source"].strip(), "empty source"
    ids = [row["id"] for row in rows]
    assert len(ids) == len(set(ids)), f"{path.name}: duplicate ids"
    return rows


def _write_csv(path: Path, header: str, data_lines: list[str]) -> None:
    path.write_text(header + "\n" + "\n".join(data_lines) + "\n", encoding="utf-8")


def test_requirements_csv_schema_ok() -> None:
    """Validation success / read happy path: tracked CSV matches schema."""
    rows = _assert_schema(REQUIREMENTS)
    assert len(rows) >= 20


def test_requirements_csv_covers_feedback_sources() -> None:
    """Success: rows cite the CMO evaluation pack form files."""
    rows = _assert_schema(REQUIREMENTS)
    sources = {row["source"] for row in rows}
    required_sources = {
        "NMHS TAC-IWXXM User Evaluation Questionnaire.docx",
        "Two-Week-Testing-Guide.docx",
        "TAC to IWXXM Test-Error Report.docx",
        "TAC-IWXXM-Comparison Checklist.docx",
        "2-WeekTest-Log TAC-IWXXM SEP 09 2026.xlsx",
    }
    missing = required_sources - sources
    assert not missing, f"missing sources: {missing}"


def test_requirements_csv_covers_success_and_failure_product_areas() -> None:
    """Success: convert/validate/accuracy (success) and error_handling (failure)."""
    rows = _assert_schema(REQUIREMENTS)
    areas = {row["product_area"] for row in rows}
    for needed in ("convert", "validate", "accuracy", "error_handling", "usability"):
        assert needed in areas, f"missing product_area {needed}"


def test_requirements_md_indexes_csv() -> None:
    """Read/query: schema companion points at the CSV matrix."""
    text = (DOCS / "requirements.md").read_text(encoding="utf-8")
    assert "requirements.csv" in text
    assert "REQ-CMO-NNN" in text


def test_readme_lists_requirements_csv() -> None:
    """Read/query: docs index lists the intake CSV."""
    text = (DOCS / "README.md").read_text(encoding="utf-8")
    assert "requirements.csv" in text
    assert "requirements.md" in text


def test_requirements_csv_rejects_bad_header(tmp_path: Path) -> None:
    """Validation failure: wrong header fails schema assert."""
    bad = tmp_path / "requirements.csv"
    _write_csv(bad, "id,wrong", ["REQ-CMO-999,x"])
    with pytest.raises(AssertionError, match="header drift"):
        _assert_schema(bad)


def test_requirements_csv_rejects_empty_required(tmp_path: Path) -> None:
    """Validation failure: empty required field is rejected."""
    bad = tmp_path / "requirements.csv"
    _write_csv(
        bad,
        HEADER,
        [
            "REQ-CMO-999,source.docx,high,convert,,criteria,open,notes",
        ],
    )
    with pytest.raises(AssertionError, match="empty requirement"):
        _assert_schema(bad)


def test_requirements_csv_rejects_bad_id(tmp_path: Path) -> None:
    """Validation failure: id that does not match REQ-CMO-NNN is rejected."""
    bad = tmp_path / "requirements.csv"
    _write_csv(
        bad,
        HEADER,
        [
            "REQ-1,source.docx,high,convert,req,criteria,open,notes",
        ],
    )
    with pytest.raises(AssertionError, match="bad id"):
        _assert_schema(bad)


def test_requirements_csv_rejects_duplicate_ids(tmp_path: Path) -> None:
    """Failure: duplicate ids are rejected."""
    bad = tmp_path / "requirements.csv"
    line = "REQ-CMO-001,source.docx,high,convert,req,criteria,open,notes"
    _write_csv(bad, HEADER, [line, line])
    with pytest.raises(AssertionError, match="duplicate ids"):
        _assert_schema(bad)


def test_requirements_csv_rejects_empty_row_payload(tmp_path: Path) -> None:
    """Validation failure / empty-row rejection: blank requirement cells fail."""
    bad = tmp_path / "requirements.csv"
    _write_csv(
        bad,
        HEADER,
        [
            ",,,,,,,",
        ],
    )
    with pytest.raises(AssertionError, match="empty"):
        _assert_schema(bad)


def test_requirements_csv_rejects_bad_priority(tmp_path: Path) -> None:
    """Validation failure: unknown priority enum is rejected."""
    bad = tmp_path / "requirements.csv"
    _write_csv(
        bad,
        HEADER,
        [
            "REQ-CMO-001,source.docx,urgent,convert,req,criteria,open,notes",
        ],
    )
    with pytest.raises(AssertionError):
        _assert_schema(bad)


def test_requirements_csv_create_row_validation_pass(tmp_path: Path) -> None:
    """Create + validation pass: appending a well-formed row keeps schema green."""
    base_rows = _assert_schema(REQUIREMENTS)
    new_id = f"REQ-CMO-{len(base_rows) + 1:03d}"
    copy = tmp_path / "requirements.csv"
    text = REQUIREMENTS.read_text(encoding="utf-8").rstrip() + "\n"
    text += (
        f"{new_id},Extra Form.docx,low,intake,"
        "Capture an additional feedback prompt.,"
        "Form field present in intake pack.,open,synthetic create\n"
    )
    copy.write_text(text, encoding="utf-8")
    rows = _assert_schema(copy)
    assert any(row["id"] == new_id for row in rows)


def test_requirements_csv_update_row_validation_pass(tmp_path: Path) -> None:
    """Update + validation pass: changing notes on an existing id stays valid."""
    rows = _assert_schema(REQUIREMENTS)
    target = rows[0]["id"]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=HEADER.split(","))
    writer.writeheader()
    for row in rows:
        payload = dict(row)
        if payload["id"] == target:
            payload["notes"] = "updated note for matrix"
        writer.writerow(payload)
    copy = tmp_path / "requirements.csv"
    copy.write_text(buffer.getvalue(), encoding="utf-8")
    updated = _assert_schema(copy)
    assert next(r for r in updated if r["id"] == target)["notes"] == (
        "updated note for matrix"
    )


def test_requirements_csv_update_row_validation_fail(tmp_path: Path) -> None:
    """Update + validation fail: clearing a required field is rejected."""
    rows = _assert_schema(REQUIREMENTS)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=HEADER.split(","))
    writer.writeheader()
    for i, row in enumerate(rows):
        payload = dict(row)
        if i == 0:
            payload["requirement"] = ""
        writer.writerow(payload)
    bad = tmp_path / "requirements.csv"
    bad.write_text(buffer.getvalue(), encoding="utf-8")
    with pytest.raises(AssertionError, match="empty requirement"):
        _assert_schema(bad)


def test_requirements_csv_delete_row_allowed(tmp_path: Path) -> None:
    """Delete + allowed: dropping one row leaves a still-valid smaller matrix."""
    rows = _assert_schema(REQUIREMENTS)
    assert len(rows) >= 2
    keep = rows[:-1]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=HEADER.split(","))
    writer.writeheader()
    for row in keep:
        writer.writerow(row)
    copy = tmp_path / "requirements.csv"
    copy.write_text(buffer.getvalue(), encoding="utf-8")
    remaining = _assert_schema(copy)
    assert len(remaining) == len(rows) - 1


def test_requirements_csv_delete_all_rows_rejected(tmp_path: Path) -> None:
    """Delete + rejected: header-only file fails (no data rows)."""
    bad = tmp_path / "requirements.csv"
    bad.write_text(HEADER + "\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="at least one data row"):
        _assert_schema(bad)
