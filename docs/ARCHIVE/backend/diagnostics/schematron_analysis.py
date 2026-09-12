"""
Diagnose Schematron XSLT2 compatibility issues.
"""

import logging
from pathlib import Path
from lxml import etree

logger = logging.getLogger(__name__)


def diagnose_schematron(version: str = "2023-1"):
    """Analyze Schematron for XSLT2 requirements."""
    sch_path = Path("/root/metar-to-IWXXM/schemas/iwxxm/2025-2/IWXXM/rule/iwxxm.sch")
    
    logger.info(f"=" * 70)
    logger.info(f"SCHEMATRON DIAGNOSTIC: {version}")
    logger.info(f"=" * 70)
    
    if not sch_path.exists():
        logger.error(f"Schematron file not found: {sch_path}")
        return {"status": "ERROR", "reason": "Schematron file missing"}
    
    logger.info(f"✓ Schematron file found: {sch_path}")
    logger.info(f"  File size: {sch_path.stat().st_size} bytes")
    
    # Parse Schematron
    try:
        sch_doc = etree.parse(str(sch_path))
        sch_root = sch_doc.getroot()
        logger.info(f"✓ Schematron XML parsing successful")
    except Exception as e:
        logger.error(f"✗ Schematron parse error: {e}")
        return {"status": "ERROR", "reason": "Parse error", "detail": str(e)}
    
    # Check query language
    query_language = sch_root.get("queryLanguage", "xslt")
    logger.info(f"Query language declared: {query_language}")
    
    # Look for XSLT2-specific features
    logger.info(f"\n[Scanning for XSLT2 features...]")
    
    xslt2_features = find_xslt2_features(sch_root)
    for feature in xslt2_features:
        logger.warning(f"⚠️  XSLT2 feature found: {feature['type']}")
        logger.debug(f"    Location: {feature['path']}")
    
    logger.info(f"Found {len(xslt2_features)} XSLT2 features")
    
    # Check for XPath 2.0 functions
    logger.info(f"\n[Scanning for XPath 2.0 functions...]")
    xpath2_functions = find_xpath2_functions(sch_root)
    for func in xpath2_functions:
        logger.warning(f"⚠️  XPath 2.0 function: {func}")
    
    logger.info(f"Found {len(xpath2_functions)} XPath 2.0 functions")
    
    # Attempt XSLT compilation
    logger.info(f"\n[Attempting XSLT compilation...]")
    xslt_compilable = False
    xslt_error = None
    try:
        xslt = etree.XSLT(sch_doc)
        logger.info(f"✓ XSLT compilation successful (likely XSLT 1.0 compatible)")
        xslt_compilable = True
    except etree.XSLTParseError as e:
        logger.error(f"✗ XSLT compilation failed:")
        error_str = str(e)
        logger.error(f"   Error: {error_str[:200]}")
        logger.debug(f"   This suggests XSLT2 features are used")
        xslt_error = error_str[:500]
        xslt_compilable = False
    
    logger.info(f"\n" + "=" * 70)
    logger.info(f"DIAGNOSIS COMPLETE")
    logger.info(f"=" * 70)
    
    return {
        "status": "SUCCESS",
        "query_language": query_language,
        "xslt_compilable": xslt_compilable,
        "xslt_error": xslt_error,
        "xslt2_features_found": len(xslt2_features),
        "xpath2_functions_found": len(xpath2_functions),
        "xslt2_features": [f['type'] for f in xslt2_features],
        "xpath2_functions": list(xpath2_functions)
    }


def find_xslt2_features(root):
    """Find XSLT2-specific features."""
    features = []
    
    # Look for xsl:for-each-group (XSLT 2.0 only)
    for elem in root.iter():
        if elem.tag.endswith("}for-each-group"):
            features.append({
                "type": "for-each-group",
                "path": elem.tag,
                "content": etree.tostring(elem).decode()[:100]
            })
    
    # Look for xsl:analyze-string (XSLT 2.0)
    for elem in root.iter():
        if elem.tag.endswith("}analyze-string"):
            features.append({
                "type": "analyze-string",
                "path": elem.tag,
                "content": etree.tostring(elem).decode()[:100]
            })
    
    # Look for xsl:result-document (XSLT 2.0)
    for elem in root.iter():
        if elem.tag.endswith("}result-document"):
            features.append({
                "type": "result-document",
                "path": elem.tag,
                "content": etree.tostring(elem).decode()[:100]
            })
    
    return features


def find_xpath2_functions(root):
    """Find XPath 2.0 function calls."""
    functions = set()
    
    xpath2_funcs = [
        "matches", "tokenize", "substring-before-last",
        "analyze-string", "count-if", "distinct-values",
        "resolve-QName", "QName", "index-of", "subsequence",
        "abs", "round-half-to-even", "avg", "sum"
    ]
    
    # Search all text content
    full_text = etree.tostring(root, encoding='unicode')
    for func in xpath2_funcs:
        if func + "(" in full_text:
            functions.add(func)
    
    return list(functions)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s: %(message)s"
    )
    
    result = diagnose_schematron("2023-1")
    print(f"\n{'='*70}")
    print(f"DIAGNOSTIC RESULT: {result['status']}")
    print(f"{'='*70}")
    if result.get('xslt2_features'):
        print(f"XSLT2 Features: {result['xslt2_features']}")
    if result.get('xpath2_functions'):
        print(f"XPath 2.0 Functions: {result['xpath2_functions']}")
