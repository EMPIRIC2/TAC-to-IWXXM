"""CLI for tac-decoding."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tac_decoding.decode import decode_tac


def main(argv: list[str] | None = None) -> int:
    """
    Decode a TAC file to JSON or plain summary.

    Returns
    -------
    int
        Process exit code (0 on success).
    """
    parser = argparse.ArgumentParser(prog="tac-decoding", description="Decode TAC to natural language")
    parser.add_argument("path", type=Path, help="Path to TAC text file")
    parser.add_argument("--product", default="METAR", help="Product type (default METAR)")
    parser.add_argument("--json", action="store_true", help="Emit JSON DecodeResult fields")
    args = parser.parse_args(argv)
    text = args.path.read_text(encoding="utf-8")
    result = decode_tac(text, product=args.product)
    if args.json:
        payload = {
            "summary": result.summary,
            "segments": [
                {
                    "code": s.code,
                    "explanation": s.explanation,
                    "start": s.start,
                    "end": s.end,
                }
                for s in result.segments
            ],
            "residuals": [{"text": r.text, "start": r.start, "end": r.end} for r in result.residuals],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(result.summary or "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
