"""F33 mass ingest helpers — caps, sniff, zip-bomb guards (EV-042 / #897).

[Corpus: product §F33] [Corpus: api] [Corpus: tech-spec]
"""

from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass
from typing import Final

# Defaults match env-contract MASS_INGEST_* (D-S050-C1 / R1).
DEFAULT_MAX_FILES: Final[int] = 200
DEFAULT_MAX_FILE_BYTES: Final[int] = 5 * 1024 * 1024
DEFAULT_MAX_TOTAL_BYTES: Final[int] = 50 * 1024 * 1024
DEFAULT_MAX_ZIP_MEMBERS: Final[int] = 200
DEFAULT_MAX_ZIP_UNCOMPRESSED_RATIO: Final[float] = 100.0

_TEXT_EXTENSIONS: Final[frozenset[str]] = frozenset(
    {".tac", ".txt", ".metar", ".speci", ".taf", ".xml", ".ahl"},
)
_BINARY_MAGIC: Final[tuple[bytes, ...]] = (
    b"\x7fELF",
    b"MZ",
    b"\x89PNG",
    b"\xff\xd8\xff",
    b"PK\x03\x04",  # nested zip inside member handled separately
)


@dataclass(frozen=True, slots=True)
class MassIngestCaps:
    """Numeric limits for one mass-ingest request."""

    max_files: int = DEFAULT_MAX_FILES
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES
    max_zip_members: int = DEFAULT_MAX_ZIP_MEMBERS
    max_zip_ratio: float = DEFAULT_MAX_ZIP_UNCOMPRESSED_RATIO


@dataclass(frozen=True, slots=True)
class MassIngestFileResult:
    """Per-file accept/reject outcome."""

    name: str
    accepted: bool
    reason: str | None = None
    size_bytes: int = 0
    content: str | None = None


def _looks_binary(sample: bytes) -> bool:
    if not sample:
        return False
    for magic in _BINARY_MAGIC:
        if sample.startswith(magic):
            # Standalone PK zip is handled as archive upload, not as a text member.
            if magic == b"PK\x03\x04":
                return True
            return True
    if b"\x00" in sample[:512]:
        return True
    return False


def _allowed_name(name: str) -> bool:
    lower = name.lower().rsplit("/", 1)[-1]
    if not lower or lower.startswith("."):
        return False
    if "." not in lower:
        return True  # extensionless TAC often used in ops
    ext = "." + lower.rsplit(".", 1)[-1]
    return ext in _TEXT_EXTENSIONS


def evaluate_text_bytes(
    name: str,
    data: bytes,
    caps: MassIngestCaps,
) -> MassIngestFileResult:
    """
    Accept or reject a single text payload under F33 caps/sniff rules.

    Parameters
    ----------
    name : str
        Original filename (may include zip member path).
    data : bytes
        Raw file bytes.
    caps : MassIngestCaps
        Request limits.

    Returns
    -------
    MassIngestFileResult
        Accepted content (UTF-8) or rejection reason.
    """
    size = len(data)
    if size > caps.max_file_bytes:
        return MassIngestFileResult(
            name=name,
            accepted=False,
            reason=f"file exceeds {caps.max_file_bytes} bytes",
            size_bytes=size,
        )
    if not _allowed_name(name):
        return MassIngestFileResult(
            name=name,
            accepted=False,
            reason="disallowed filename or extension",
            size_bytes=size,
        )
    if _looks_binary(data[:1024]):
        return MassIngestFileResult(
            name=name,
            accepted=False,
            reason="binary or executable content rejected",
            size_bytes=size,
        )
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return MassIngestFileResult(
            name=name,
            accepted=False,
            reason="content is not valid UTF-8 text",
            size_bytes=size,
        )
    return MassIngestFileResult(
        name=name,
        accepted=True,
        size_bytes=size,
        content=text,
    )


def expand_zip_bytes(
    archive_name: str,
    data: bytes,
    caps: MassIngestCaps,
) -> list[MassIngestFileResult]:
    """
    Unpack a zip under zip-bomb guards and evaluate each member.

    Parameters
    ----------
    archive_name : str
        Uploaded zip filename (for error context).
    data : bytes
        Zip archive bytes.
    caps : MassIngestCaps
        Limits including member count and compression ratio.

    Returns
    -------
    list[MassIngestFileResult]
        One result per member, or a single reject for the archive.
    """
    if len(data) > caps.max_total_bytes:
        return [
            MassIngestFileResult(
                name=archive_name,
                accepted=False,
                reason=f"zip exceeds {caps.max_total_bytes} bytes compressed",
                size_bytes=len(data),
            )
        ]
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            infos = [i for i in zf.infolist() if not i.is_dir()]
            if len(infos) > caps.max_zip_members:
                return [
                    MassIngestFileResult(
                        name=archive_name,
                        accepted=False,
                        reason=f"zip has more than {caps.max_zip_members} members",
                        size_bytes=len(data),
                    )
                ]
            total_uncompressed = sum(max(i.file_size, 0) for i in infos)
            if total_uncompressed > caps.max_total_bytes:
                return [
                    MassIngestFileResult(
                        name=archive_name,
                        accepted=False,
                        reason=f"zip uncompressed size exceeds {caps.max_total_bytes} bytes",
                        size_bytes=total_uncompressed,
                    )
                ]
            if len(data) > 0 and total_uncompressed / len(data) > caps.max_zip_ratio:
                return [
                    MassIngestFileResult(
                        name=archive_name,
                        accepted=False,
                        reason="zip compression ratio looks like a zip bomb",
                        size_bytes=total_uncompressed,
                    )
                ]
            results: list[MassIngestFileResult] = []
            for info in infos:
                member_name = info.filename
                if ".." in member_name.replace("\\", "/").split("/"):
                    results.append(
                        MassIngestFileResult(
                            name=member_name,
                            accepted=False,
                            reason="path traversal rejected",
                            size_bytes=info.file_size,
                        )
                    )
                    continue
                raw = zf.read(info)
                results.append(evaluate_text_bytes(member_name, raw, caps))
            return results
    except zipfile.BadZipFile:
        return [
            MassIngestFileResult(
                name=archive_name,
                accepted=False,
                reason="invalid zip archive",
                size_bytes=len(data),
            )
        ]


__all__ = [
    "MassIngestCaps",
    "MassIngestFileResult",
    "DEFAULT_MAX_FILE_BYTES",
    "DEFAULT_MAX_FILES",
    "DEFAULT_MAX_TOTAL_BYTES",
    "evaluate_text_bytes",
    "expand_zip_bytes",
]
