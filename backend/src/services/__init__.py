"""Service layer for conversion operations."""
from typing import List, Tuple

from utilities.conversion import convert_metar_tac, ConversionError
from schemas.conversion import ConversionResult


async def process_manual_text(manual_text: str) -> Tuple[List[ConversionResult], List[str]]:
    """Process manually entered METAR text.

    Args:
        manual_text: METAR TAC text entered by user

    Returns:
        Tuple of (results, errors)
    """
    results = []
    errors = []

    if manual_text.strip():
        try:
            xml_text = convert_metar_tac(manual_text.strip())
            results.append(
                ConversionResult(
                    name="manual_input.txt",
                    content=xml_text,
                    source="manual",
                    size_bytes=len(xml_text.encode("utf-8")),
                )
            )
        except ConversionError as e:
            errors.append(f"manual_input: {e}")

    return results, errors


__all__ = ["process_manual_text"]
