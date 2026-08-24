#!/usr/bin/env python3
"""Extract page-marked text from a PDF into sibling fulltext.txt + pages.jsonl.

Usage:
  python3 extract_pdf.py path/to/file.pdf
  python3 extract_pdf.py path/to/file.pdf --out-dir path/to/dir
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def extract(pdf_path: Path, out_dir: Path) -> tuple[Path, Path]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "pypdf is required. Install with: pip install pypdf  (or use project uv env)"
        ) from exc

    if not pdf_path.is_file():
        raise SystemExit(f"PDF not found: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    n_pages = len(reader.pages)
    if n_pages == 0:
        raise SystemExit(f"PDF has zero pages: {pdf_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    fulltext_path = out_dir / "fulltext.txt"
    pages_path = out_dir / "pages.jsonl"

    parts: list[str] = []
    with pages_path.open("w", encoding="utf-8") as jl:
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            parts.append(f"\n\n===== PAGE {i} =====\n\n{text}")
            jl.write(json.dumps({"page": i, "text": text}, ensure_ascii=False) + "\n")
            if i % 25 == 0 or i == n_pages:
                print(f"  extracted {i}/{n_pages}", file=sys.stderr)

    fulltext_path.write_text("".join(parts), encoding="utf-8")
    return fulltext_path, pages_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="Path to PDF file")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (default: same directory as the PDF)",
    )
    args = parser.parse_args()
    pdf_path = args.pdf.resolve()
    out_dir = (args.out_dir or pdf_path.parent).resolve()

    print(f"Reading {pdf_path}", file=sys.stderr)
    fulltext_path, pages_path = extract(pdf_path, out_dir)
    print(f"Wrote {fulltext_path} ({fulltext_path.stat().st_size} bytes)")
    print(f"Wrote {pages_path} ({pages_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
