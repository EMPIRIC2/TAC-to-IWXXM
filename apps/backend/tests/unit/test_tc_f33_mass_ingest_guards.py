"""TC-F33-002/003 — mass ingest caps, sniff, zip-bomb (EV-042).

[Corpus: product §F33] [Corpus: tests]
"""

from __future__ import annotations

import io
import zipfile

from src.services.mass_ingest import MassIngestCaps, evaluate_text_bytes, expand_zip_bytes


def test_tc_f33_002_accepts_utf8_tac_under_caps() -> None:
    caps = MassIngestCaps(max_file_bytes=1000, max_files=10, max_total_bytes=5000)
    data = b"METAR KJFK 121251Z 18012KT 10SM=\n"
    result = evaluate_text_bytes("sample.tac", data, caps)
    assert result.accepted is True
    assert result.content is not None
    assert "METAR" in result.content


def test_tc_f33_002_rejects_oversize_file() -> None:
    caps = MassIngestCaps(max_file_bytes=16, max_files=10, max_total_bytes=5000)
    result = evaluate_text_bytes("big.tac", b"x" * 32, caps)
    assert result.accepted is False
    assert result.reason is not None
    assert "exceeds" in result.reason


def test_tc_f33_003_rejects_elf_binary() -> None:
    caps = MassIngestCaps()
    result = evaluate_text_bytes("evil.tac", b"\x7fELF" + b"\x00" * 20, caps)
    assert result.accepted is False
    assert result.reason is not None
    assert "binary" in result.reason.lower()


def test_tc_f33_003_rejects_zip_bomb_ratio() -> None:
    caps = MassIngestCaps(
        max_files=50,
        max_file_bytes=10_000_000,
        max_total_bytes=10_000_000,
        max_zip_members=50,
        max_zip_ratio=5.0,
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Highly compressible zeros → huge ratio vs small compressed size.
        zf.writestr("zeros.tac", "0" * 200_000)
    data = buf.getvalue()
    results = expand_zip_bytes("bomb.zip", data, caps)
    assert len(results) == 1
    assert results[0].accepted is False
    assert results[0].reason is not None
    assert "bomb" in results[0].reason.lower() or "ratio" in results[0].reason.lower()


def test_tc_f33_003_expands_valid_zip_member() -> None:
    caps = MassIngestCaps()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("a.tac", "METAR KJFK 121251Z=\n")
    results = expand_zip_bytes("ok.zip", buf.getvalue(), caps)
    assert len(results) == 1
    assert results[0].accepted is True
    assert results[0].content is not None
