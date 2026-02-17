"""
Helper utility for extracting ICAO airport codes from TAC messages.
"""
import re
from typing import Optional


def extract_airport_code(tac_message: str) -> Optional[str]:
    """
    Extract ICAO airport code from TAC METAR/SPECI message.
    
    Args:
        tac_message: TAC format METAR or SPECI message
        
    Returns:
        4-letter ICAO airport code, or None if not found
        
    Examples:
        >>> extract_airport_code("METAR KJFK 131051Z 18012KT 10SM FEW250")
        'KJFK'
        >>> extract_airport_code("SPECI EGLL 111520Z 27015KT 9999 BKN025")
        'EGLL'
    """
    # Pattern:METAR or SPECI keyword, followed by 4-letter ICAO code
    # ICAO codes are 4 uppercase letters
    pattern = r'(?:METAR|SPECI)\s+([A-Z]{4})\s+'
    
    match = re.search(pattern, tac_message.upper())
    if match:
        return match.group(1)
    
    return None
