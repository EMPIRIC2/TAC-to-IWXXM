"""CLI for tac-decoding."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tac_decoding.decode import decode_tac
from tac_decoding.overlay_check import check_pack_overlay_dir


def main(argv: list[str] | None = None) -> int:
    """
    Decode a TAC file to JSON or plain summary, or check a pack overlay directory.

    Returns
    -------
    int
        Process exit code (0 on success).
    """
    parser = argparse.ArgumentParser(prog="tac-decoding", description="Decode TAC to natural language")
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        help="Path to TAC text file (required unless --check-overlay)",
    )
    parser.add_argument("--product", default="METAR", help="Product type (default METAR)")
    parser.add_argument("--json", action="store_true", help="Emit JSON DecodeResult fields")
    parser.add_argument(
        "--check-overlay",
        type=Path,
        metavar="DIR",
        help="Fail-closed load of pack YAML overlays in DIR (no TAC decode)",
    )
    args = parser.parse_args(argv)

    if args.check_overlay is not None:
        try:
            check_pack_overlay_dir(args.check_overlay)
        except Exception as exc:
            print(f"error: pack overlay check failed: {exc}", file=sys.stderr)
            return 1
        print(f"ok pack overlay {args.check_overlay}")
        return 0

    if args.path is None:
        parser.error("path is required unless --check-overlay is set")

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
