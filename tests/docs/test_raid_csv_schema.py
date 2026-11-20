"""RAID CSV schema integrity for docs/{issues,risks,assumptions,decisions}.csv.

Covers validation success (tracked files) and validation failure (bad header /
missing required fields). Mutation modes are N/A: these files are cite-only
corpus logs, not a create/update/delete API.
"""

from __future__ import annotations

import csv
import io
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"

ISSUES_HEADER = "id,date,status,summary,owner,links,corpus_cite,notes,severity"
RISKS_HEADER = (
    "id,date,status,summary,owner,links,corpus_cite,notes,likelihood,impact,mitigation"
)
ASSUMPTIONS_HEADER = "id,date,status,summary,owner,links,corpus_cite,notes"
DECISIONS_HEADER = "id,date,status,summary,owner,links,corpus_cite,notes,decision"

ID_PATTERNS = {
    "issues.csv": re.compile(r"^I-\d{3}$"),
    "risks.csv": re.compile(r"^R-\d{3}$"),
    "assumptions.csv": re.compile(r"^A-\d{3}$"),
    "decisions.csv": re.compile(r"^D-\d{3}$"),
}

REQUIRED_NONEMPTY = ("id", "date", "status", "summary", "owner", "corpus_cite")


def _read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    text = path.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text))
    assert reader.fieldnames is not None
    return list(reader.fieldnames), list(reader)


def _assert_schema(
    path: Path,
    *,
    expected_header: str,
    id_pattern: re.Pattern[str],
) -> None:
    header_line = path.read_text(encoding="utf-8").splitlines()[0]
    assert header_line == expected_header, f"{path.name}: header drift"
    _, rows = _read_rows(path)
    assert rows, f"{path.name}: expected at least one data row"
    for row in rows:
        for key in REQUIRED_NONEMPTY:
            assert row.get(key, "").strip(), f"{path.name}: empty {key}"
        assert id_pattern.match(row["id"]), f"{path.name}: bad id {row['id']!r}"
        assert "[Corpus:" in row["corpus_cite"], (
            f"{path.name}: corpus_cite must cite [Corpus: …]"
        )
    ids = [row["id"] for row in rows]
    assert len(ids) == len(set(ids)), f"{path.name}: duplicate ids"


def test_issues_csv_schema_ok() -> None:
    """Validation success: issues.csv matches RAID header and required fields."""
    _assert_schema(
        DOCS / "issues.csv",
        expected_header=ISSUES_HEADER,
        id_pattern=ID_PATTERNS["issues.csv"],
    )


def test_risks_csv_schema_ok() -> None:
    """Validation success: risks.csv matches RAID header and required fields."""
    _assert_schema(
        DOCS / "risks.csv",
        expected_header=RISKS_HEADER,
        id_pattern=ID_PATTERNS["risks.csv"],
    )


def test_assumptions_and_decisions_csv_schema_ok() -> None:
    """Validation success: sibling RAID CSVs keep header and id contracts."""
    _assert_schema(
        DOCS / "assumptions.csv",
        expected_header=ASSUMPTIONS_HEADER,
        id_pattern=ID_PATTERNS["assumptions.csv"],
    )
    _assert_schema(
        DOCS / "decisions.csv",
        expected_header=DECISIONS_HEADER,
        id_pattern=ID_PATTERNS["decisions.csv"],
    )


def test_automation_gap_raid_rows_present() -> None:
    """Read/query happy path: I-003 / R-003 link #884 automation gaps."""
    _, issues = _read_rows(DOCS / "issues.csv")
    _, risks = _read_rows(DOCS / "risks.csv")
    i003 = next(row for row in issues if row["id"] == "I-003")
    r003 = next(row for row in risks if row["id"] == "R-003")
    assert "#884" in i003["links"]
    assert "domain-contract.md" in i003["links"]
    assert "#884" in r003["links"]
    assert "domain-contract.md" in r003["links"]
    domain = (DOCS / "domain-contract.md").read_text(encoding="utf-8")
    assert "Automation gaps" in domain
    assert "I-003" in domain
    assert "R-003" in domain


def test_raid_csv_rejects_bad_header(tmp_path: Path) -> None:
    """Validation failure: wrong header fails schema assert."""
    bad = tmp_path / "issues.csv"
    bad.write_text("id,wrong\nI-999,x\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="header drift"):
        _assert_schema(
            bad,
            expected_header=ISSUES_HEADER,
            id_pattern=ID_PATTERNS["issues.csv"],
        )


def test_raid_csv_rejects_empty_required(tmp_path: Path) -> None:
    """Validation failure: empty required field is rejected."""
    bad = tmp_path / "issues.csv"
    bad.write_text(
        ISSUES_HEADER + "\n"
        "I-999,2026-11-20,open,,docs,links,[Corpus: domain],notes,low\n",
        encoding="utf-8",
    )
    with pytest.raises(AssertionError, match="empty summary"):
        _assert_schema(
            bad,
            expected_header=ISSUES_HEADER,
            id_pattern=ID_PATTERNS["issues.csv"],
        )


def test_raid_csv_rejects_bad_id(tmp_path: Path) -> None:
    """Validation failure: id that does not match I-NNN is rejected."""
    bad = tmp_path / "issues.csv"
    bad.write_text(
        ISSUES_HEADER + "\n"
        "ISSUE-1,2026-11-20,open,summary,docs,links,[Corpus: domain],notes,low\n",
        encoding="utf-8",
    )
    with pytest.raises(AssertionError, match="bad id"):
        _assert_schema(
            bad,
            expected_header=ISSUES_HEADER,
            id_pattern=ID_PATTERNS["issues.csv"],
        )


def test_domain_contract_anchor_and_cross_links() -> None:
    """Read/query: ACCESS / RULE_SOURCE docs link the automation-gaps section."""
    access = (ROOT / "config" / "rules" / "ACCESS_AND_CITATION.md").read_text(
        encoding="utf-8"
    )
    sources = (ROOT / "config" / "rules" / "RULE_SOURCE_URLS.md").read_text(
        encoding="utf-8"
    )
    assert "automation-gaps-outside-live-feed-refresh" in access
    assert "#884" in access
    assert "automation-gaps-outside-live-feed-refresh" in sources
    assert "#884" in sources
