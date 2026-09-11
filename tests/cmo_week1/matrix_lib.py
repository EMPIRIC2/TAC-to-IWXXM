#!/usr/bin/env python3
"""Run CMO Week 1 TAC corpus through convert + IWXXM validate.

[Corpus: product §F6] [Corpus: product §F2] [Corpus: tests]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from iwxxm_validate import validate

from tac2iwxxm import convert

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "tests" / "fixtures" / "cmo_week1"
DEFAULT_EVIDENCE = (
    Path.home()
    / ".cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-cmo-week1-test-sets/evidence"
)

AHL_RE = re.compile(r"^[A-Z]{4}\d{2}\s+[A-Z]{4}\s+\d{6}\s*$")
TITLE_RE = re.compile(r"^Week\s+1", re.I)
PRODUCT_START = re.compile(
    r"^(?:METAR|SPECI|TAF|[A-Z]{4}\s+SIGMET|SIGA0[A-Z0-9]|[A-Z]{4}\s+\d{6}Z)\b"
)


@dataclass
class Message:
    dataset: str
    index: int
    ahl: str | None
    tac: str
    product: str


@dataclass
class Row:
    dataset: str
    index: int
    ahl: str | None
    product: str
    product_inferred: str
    tac: str
    convert_ok: bool
    validate_ok: bool | None
    xml_path: str | None
    convert_codes: list[str]
    validate_codes: list[str]
    disposition: str
    error: str | None = None


def _infer_product(tac: str, dataset_default: str) -> str:
    head = tac.lstrip()
    if head.startswith("SPECI"):
        return "SPECI"
    if head.startswith("METAR"):
        return "METAR"
    if head.startswith("TAF"):
        return "TAF"
    if "SIGMET" in head[:80] or head.startswith("SIGA0"):
        return "SIGMET"
    # Bare ICAO observation (authoritative SPECI-set oddity)
    if re.match(r"^[A-Z]{4}\s+\d{6}Z\b", head):
        return dataset_default
    return dataset_default


def parse_ahl_bulletin(
    text: str, *, dataset: str, default_product: str
) -> list[Message]:
    """Parse AHL + body blocks from an authoritative extract."""
    lines = text.splitlines()
    messages: list[Message] = []
    i = 0
    idx = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        if not line or TITLE_RE.match(line):
            i += 1
            continue
        ahl: str | None = None
        if AHL_RE.match(line):
            ahl = line
            i += 1
            # skip blank lines after AHL
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i >= len(lines):
                break
            # US oceanic abbreviated heading after AHL
            if lines[i].strip().startswith("SIGA0"):
                body_lines = [lines[i].strip()]
                i += 1
            else:
                body_lines = []
        elif PRODUCT_START.match(line) or "SIGMET" in line:
            body_lines = []
        else:
            i += 1
            continue

        # Accumulate body until next AHL or blank+AHL or next product start after content
        while i < len(lines):
            cur = lines[i]
            cur_s = cur.strip()
            if not cur_s:
                # peek ahead: blank then AHL → end; else keep (SIGMET wrapping)
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and AHL_RE.match(lines[j].strip()):
                    break
                if j < len(lines) and (
                    PRODUCT_START.match(lines[j].strip())
                    or lines[j].strip().startswith("SYGC SIGMET")
                ):
                    # next message without AHL
                    break
                body_lines.append("")
                i += 1
                continue
            if AHL_RE.match(cur_s) and body_lines:
                break
            if (
                body_lines
                and default_product != "SIGMET"
                and AHL_RE.match(cur_s) is None
                and PRODUCT_START.match(cur_s)
                and not cur_s.startswith(
                    ("FEW", "SCT", "BKN", "OVC", "PROB", "BECMG", "TEMPO")
                )
            ):
                # METAR/SPECI/TAF are usually one logical line; if a new product keyword
                # appears without AHL, start a new message only when we already have body
                # and this looks like a fresh report (rare in these files).
                break
            body_lines.append(cur_s)
            i += 1
            # For METAR/SPECI/TAF: typically single line after AHL
            if default_product in {"METAR", "SPECI", "TAF"} and body_lines:
                # Keep going only if next non-blank is continuation (no AHL, no new product)
                j = i
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j >= len(lines) or AHL_RE.match(lines[j].strip()):
                    break
                nxt = lines[j].strip()
                if PRODUCT_START.match(nxt) or nxt.startswith(
                    ("METAR", "SPECI", "TAF", "SATD", "SAAT", "FTCA", "FTLC")
                ):
                    break
                # TAF may wrap; keep collecting until blank or AHL
                if default_product == "TAF":
                    continue
                break

        tac = "\n".join(x for x in body_lines if x is not None).strip()
        if not tac:
            continue
        product = _infer_product(tac, default_product)
        messages.append(
            Message(dataset=dataset, index=idx, ahl=ahl, tac=tac, product=product)
        )
        idx += 1
    return messages


def parse_sigmet_file(text: str) -> list[Message]:
    """SIGMET extracts: AHL optional; multi-line bodies; SIGA0 abbreviated heading."""
    lines = [ln.rstrip() for ln in text.splitlines()]
    messages: list[Message] = []
    i = 0
    idx = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or TITLE_RE.match(line):
            i += 1
            continue
        ahl: str | None = None
        body: list[str] = []
        if AHL_RE.match(line):
            ahl = line
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i < len(lines) and lines[i].strip().startswith("SIGA0"):
                body.append(lines[i].strip())
                i += 1
        # body until next AHL or orphan SIGMET start
        while i < len(lines):
            cur = lines[i].strip()
            if not cur:
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j >= len(lines):
                    break
                nxt = lines[j].strip()
                if AHL_RE.match(nxt):
                    break
                # orphan next SIGMET (no AHL)
                if re.match(r"^[A-Z]{4}\s+SIGMET\b", nxt):
                    break
                i += 1
                continue
            if AHL_RE.match(cur) and body:
                break
            # Orphan-to-orphan: new CCCC SIGMET starts when body already has SIGMET
            if (
                body
                and ahl is None
                and re.match(r"^[A-Z]{4}\s+SIGMET\b", cur)
                and any("SIGMET" in b for b in body)
            ):
                break
            body.append(cur)
            i += 1
        tac = "\n".join(body).strip()
        if not tac:
            continue
        messages.append(
            Message(dataset="sigmet", index=idx, ahl=ahl, tac=tac, product="SIGMET")
        )
        idx += 1
    return messages


def load_corpus() -> list[Message]:
    out: list[Message] = []
    out.extend(
        parse_ahl_bulletin(
            (FIXTURES / "metar.txt").read_text(),
            dataset="metar",
            default_product="METAR",
        )
    )
    out.extend(
        parse_ahl_bulletin(
            (FIXTURES / "speci.txt").read_text(),
            dataset="speci",
            default_product="SPECI",
        )
    )
    out.extend(
        parse_ahl_bulletin(
            (FIXTURES / "taf.txt").read_text(), dataset="taf", default_product="TAF"
        )
    )
    out.extend(parse_sigmet_file((FIXTURES / "sigmet.txt").read_text()))
    return out


def _disposition(msg: Message, convert_ok: bool, validate_ok: bool | None) -> str:
    tac = msg.tac
    # Authoritative intentional negatives / oddities (source must not be rewritten)
    if msg.dataset == "speci" and tac.startswith("METAR "):
        return "authoritative_cross_product"
    if (
        msg.dataset == "speci"
        and re.match(r"^[A-Z]{4}\s+\d{6}Z\b", tac)
        and not tac.startswith("SPECI")
    ):
        return "authoritative_missing_product_keyword"
    # EMPO typo must not match TEMPO (substring trap)
    if msg.dataset == "taf" and re.search(r"(?<![A-Z])EMPO(?![A-Z])", tac):
        return "authoritative_token_typo"
    if msg.dataset == "taf" and tac.rstrip().endswith("TEMPO 0904/0910"):
        return "authoritative_truncated"
    if re.search(r"(?<![A-Z])NOISG(?![A-Z])", tac) or "VIS16KIM" in tac:
        return "authoritative_token_typo"
    if msg.dataset == "sigmet" and tac.lstrip().startswith("SIGA0"):
        return "authoritative_us_oceanic_siga0"
    if convert_ok and validate_ok:
        return "pass"
    if convert_ok and validate_ok is False:
        return "validate_fail"
    if not convert_ok:
        return "convert_fail"
    return "convert_ok_no_validate"


def run_matrix(
    *,
    evidence: Path,
    profile: str = "annex3",
    iwxxm_version: str = "2025-2",
    limit: int | None = None,
) -> dict:
    evidence.mkdir(parents=True, exist_ok=True)
    xml_root = evidence / "iwxxm"
    xml_root.mkdir(parents=True, exist_ok=True)
    sample_dir = FIXTURES / "samples"
    sample_dir.mkdir(parents=True, exist_ok=True)

    messages = load_corpus()
    if limit is not None:
        messages = messages[:limit]

    rows: list[Row] = []
    samples_written: set[str] = set()

    for msg in messages:
        inferred = _infer_product(msg.tac, msg.product)
        convert_codes: list[str] = []
        validate_codes: list[str] = []
        xml_path: str | None = None
        convert_ok = False
        validate_ok: bool | None = None
        err: str | None = None
        try:
            result = convert(
                msg.tac,
                product=inferred,
                profile=profile,
                iwxxm_version=iwxxm_version,
            )
            convert_ok = bool(result.ok)
            convert_codes = [i.code for i in result.issues]
            if result.xml:
                rel = f"{msg.dataset}/{msg.index:04d}.xml"
                out_path = xml_root / rel
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(result.xml, encoding="utf-8")
                xml_path = str(out_path)
                if convert_ok and inferred not in samples_written:
                    (sample_dir / f"{inferred.lower()}_sample.xml").write_text(
                        result.xml, encoding="utf-8"
                    )
                    samples_written.add(inferred)
                v = validate(result.xml, iwxxm_version=iwxxm_version, profile=profile)
                validate_ok = bool(v.ok)
                validate_codes = [i.code for i in v.issues]
        except Exception as exc:
            err = f"{type(exc).__name__}: {exc}"
            convert_ok = False

        rows.append(
            Row(
                dataset=msg.dataset,
                index=msg.index,
                ahl=msg.ahl,
                product=msg.product,
                product_inferred=inferred,
                tac=msg.tac,
                convert_ok=convert_ok,
                validate_ok=validate_ok,
                xml_path=xml_path,
                convert_codes=convert_codes,
                validate_codes=validate_codes,
                disposition=_disposition(msg, convert_ok, validate_ok),
                error=err,
            )
        )

    by_ds: dict[str, Counter[str]] = {}
    for r in rows:
        by_ds.setdefault(r.dataset, Counter())[r.disposition] += 1

    summary = {
        "profile": profile,
        "iwxxm_version": iwxxm_version,
        "total": len(rows),
        "convert_ok": sum(1 for r in rows if r.convert_ok),
        "validate_ok": sum(1 for r in rows if r.validate_ok),
        "by_dataset": {k: dict(v) for k, v in by_ds.items()},
        "message_counts": dict(Counter(r.dataset for r in rows)),
    }
    report = {"summary": summary, "rows": [asdict(r) for r in rows]}
    report_path = evidence / "matrix-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    # Compact copy in fixtures only for full corpus runs (pytest pins this artifact)
    if limit is None:
        (FIXTURES / "matrix-summary.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )
    return report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--profile", default="annex3")
    p.add_argument("--iwxxm-version", default="2025-2")
    args = p.parse_args(argv)
    report = run_matrix(
        evidence=args.evidence,
        profile=args.profile,
        iwxxm_version=args.iwxxm_version,
        limit=args.limit,
    )
    s = report["summary"]
    print(json.dumps(s, indent=2))
    print(f"wrote {args.evidence / 'matrix-report.json'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
