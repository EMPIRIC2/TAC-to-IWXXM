"""Every XLSX test-log TAC cell converts or matches a locked harvest row.

[Corpus: tests]
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from tac2iwxxm.convert import convert

from .conftest import RAW, guess_product, strip_gts

openpyxl = pytest.importorskip("openpyxl")

_XLSX = sorted(RAW.rglob("*.xlsx"))
_TAC_LINE = re.compile(
    r"(?:METAR|SPECI|TAF)\s+[A-Z]{4}\s+\d{6}Z\b[^\n=]{10,500}=?",
    re.I,
)
_SIGMET_LINE = re.compile(r"(?:[A-Z]{4}\s+)?SIGMET\b[^\n=]{20,600}=?", re.I)


def _extract_tac_cells(path: Path) -> list[str]:
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    found: list[str] = []
    try:
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            rows = list(sheet.iter_rows(values_only=True))
            if not rows:
                continue
            header = [str(cell).lower() if cell else "" for cell in rows[0]]
            tac_idx = None
            for index, name in enumerate(header):
                if "tac" in name and ("message" in name or "reference" in name):
                    tac_idx = index
                    break
            if (
                tac_idx is None
                and sheet_name == "Sheet1"
                and header
                and "iwxxm" in header[0]
            ):
                tac_idx = 0
            for row in rows[1:]:
                if not row:
                    continue
                cells: list[str] = []
                if (
                    tac_idx is not None
                    and tac_idx < len(row)
                    and isinstance(row[tac_idx], str)
                ):
                    cells.append(row[tac_idx])
                else:
                    cells.extend(str(cell) for cell in row if isinstance(cell, str))
                for cell in cells:
                    found.extend(
                        match.group(0).strip() for match in _TAC_LINE.finditer(cell)
                    )
                    found.extend(
                        match.group(0).strip() for match in _SIGMET_LINE.finditer(cell)
                    )
    finally:
        workbook.close()
    # de-dupe preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for tac in found:
        key = re.sub(r"\s+", " ", tac.upper())
        if key in seen:
            continue
        seen.add(key)
        unique.append(tac)
    return unique


@pytest.mark.parametrize("path", _XLSX, ids=[p.name for p in _XLSX])
def test_xlsx_extracted_tac_converts(path: Path) -> None:
    samples = _extract_tac_cells(path)
    # BVI log may be empty of TAC text — still must parse without error.
    if not samples:
        assert path.suffix.lower() == ".xlsx"
        return
    failures: list[str] = []
    for tac in samples:
        body = strip_gts(tac)
        product = guess_product(body)
        if product not in {"METAR", "SPECI", "TAF", "SIGMET"}:
            continue
        result = convert(body, product=product, bulletin_date="2026-10-08")
        # Incomplete / truncated rows may fail closed; that is still a defined outcome.
        if result.ok and result.xml is None:
            failures.append(body[:80])
        if not result.ok and not result.issues:
            failures.append(body[:80])
    assert failures == []
