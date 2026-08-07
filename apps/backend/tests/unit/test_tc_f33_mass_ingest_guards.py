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


def test_tc_f33_002_rejects_disallowed_extension() -> None:
    caps = MassIngestCaps()
    result = evaluate_text_bytes("payload.exe", b"METAR KJFK=\n", caps)
    assert result.accepted is False
    assert result.reason is not None
    assert "disallowed" in result.reason


def test_tc_f33_002_rejects_invalid_utf8() -> None:
    caps = MassIngestCaps()
    result = evaluate_text_bytes("bad.tac", b"\xff\xfe METAR", caps)
    assert result.accepted is False
    assert result.reason is not None
    assert "UTF-8" in result.reason


def test_tc_f33_002_rejects_mz_and_png_magic() -> None:
    caps = MassIngestCaps()
    mz = evaluate_text_bytes("win.tac", b"MZ" + b"\x00" * 20, caps)
    png = evaluate_text_bytes("img.tac", b"\x89PNG\r\n\x1a\n" + b"\x00" * 8, caps)
    jpeg = evaluate_text_bytes("photo.tac", b"\xff\xd8\xff" + b"\x00" * 8, caps)
    nested_zip = evaluate_text_bytes("nested.tac", b"PK\x03\x04" + b"\x00" * 8, caps)
    empty = evaluate_text_bytes("empty.tac", b"", caps)
    assert mz.accepted is False
    assert png.accepted is False
    assert jpeg.accepted is False
    assert nested_zip.accepted is False
    assert empty.accepted is True  # empty UTF-8 text is allowed
    assert mz.reason is not None and "binary" in mz.reason.lower()
    assert nested_zip.reason is not None and "binary" in nested_zip.reason.lower()


def test_tc_f33_002_accepts_extensionless_and_rejects_dotfile() -> None:
    caps = MassIngestCaps()
    ok = evaluate_text_bytes("KJFK", b"METAR KJFK=\n", caps)
    hidden = evaluate_text_bytes(".hidden.tac", b"METAR KJFK=\n", caps)
    assert ok.accepted is True
    assert hidden.accepted is False


def test_tc_f33_003_rejects_zip_too_many_members() -> None:
    caps = MassIngestCaps(max_zip_members=1, max_files=10)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("a.tac", "METAR A=\n")
        zf.writestr("b.tac", "METAR B=\n")
    results = expand_zip_bytes("many.zip", buf.getvalue(), caps)
    assert len(results) == 1
    assert results[0].accepted is False
    assert results[0].reason is not None
    assert "more than" in results[0].reason


def test_tc_f33_003_rejects_zip_uncompressed_cap() -> None:
    caps = MassIngestCaps(
        max_file_bytes=50_000,
        max_total_bytes=2_000,
        max_zip_members=10,
        max_zip_ratio=10_000.0,
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("a.tac", "0" * 5_000)
    data = buf.getvalue()
    assert len(data) <= 2_000
    results = expand_zip_bytes("big.zip", data, caps)
    assert len(results) == 1
    assert results[0].accepted is False
    assert results[0].reason is not None
    assert "uncompressed" in results[0].reason


def test_tc_f33_003_rejects_zip_compressed_cap() -> None:
    caps = MassIngestCaps(max_total_bytes=8)
    results = expand_zip_bytes("tiny-cap.zip", b"PK" + b"\x00" * 20, caps)
    assert len(results) == 1
    assert results[0].accepted is False


def test_tc_f33_003_rejects_path_traversal_member() -> None:
    caps = MassIngestCaps()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("../etc/passwd.tac", "METAR KJFK=\n")
    results = expand_zip_bytes("trav.zip", buf.getvalue(), caps)
    assert len(results) == 1
    assert results[0].accepted is False
    assert results[0].reason is not None
    assert "traversal" in results[0].reason


def test_tc_f33_003_rejects_bad_zip_bytes() -> None:
    caps = MassIngestCaps()
    results = expand_zip_bytes("broken.zip", b"not-a-zip", caps)
    assert len(results) == 1
    assert results[0].accepted is False
    assert results[0].reason is not None
    assert "invalid zip" in results[0].reason
