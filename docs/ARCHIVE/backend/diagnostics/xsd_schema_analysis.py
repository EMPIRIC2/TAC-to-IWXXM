"""
Diagnose XSD schema issues without modifying WMO repos.
"""

import logging
from pathlib import Path
from lxml import etree

logger = logging.getLogger(__name__)


def diagnose_xsd_schema(version: str = "2023-1"):
    """Analyze XSD schema for issues."""
    schema_path = Path("/root/metar-to-IWXXM/schemas/iwxxm/2025-2/IWXXM/iwxxm.xsd")
    
    logger.info(f"=" * 70)
    logger.info(f"XSD SCHEMA DIAGNOSTIC: {version}")
    logger.info(f"=" * 70)
    
    # 1. Check file existence
    if not schema_path.exists():
        logger.error(f"Schema file not found: {schema_path}")
        return {"status": "ERROR", "reason": "Schema file missing"}
    
    logger.info(f"✓ Schema file found: {schema_path}")
    logger.info(f"  File size: {schema_path.stat().st_size} bytes")
    
    # 2. Parse XML structure
    try:
        tree = etree.parse(str(schema_path))
        root = tree.getroot()
        logger.info(f"✓ XML parsing successful")
        logger.info(f"  Root tag: {root.tag}")
        logger.debug(f"  Root attribs: {root.attrib}")
    except etree.XMLSyntaxError as e:
        logger.error(f"✗ XML Parse error: {e}")
        return {"status": "ERROR", "reason": "XML parse error", "detail": str(e)}
    
    # 3. Find problematic QName elements
    logger.info(f"\n[Searching for QName resolution issues...]")
    
    qname_issues = find_qname_issues(root)
    for issue in qname_issues:
        logger.warning(f"⚠️  QName Issue: {issue['element']}")
        logger.debug(f"    Path: {issue['path']}")
        logger.debug(f"    Referenced: {issue['referenced_element']}")
        logger.debug(f"    Namespace: {issue['namespace']}")
    
    # 4. Check namespace declarations
    logger.info(f"\n[Checking namespace declarations...]")
    namespaces = extract_namespaces(root)
    for prefix, uri in namespaces.items():
        logger.debug(f"  {prefix}: {uri}")
    
    logger.info(f"Total namespaces: {len(namespaces)}")
    
    # 5. Check for external schema imports/includes
    logger.info(f"\n[Checking schema imports/includes...]")
    imports = find_schema_imports(root)
    for imp in imports:
        logger.debug(f"  Import: {imp['location']}")
        imp_path = schema_path.parent / imp['location']
        if imp_path.exists():
            logger.info(f"    ✓ Location exists")
        else:
            logger.warning(f"    ✗ Location NOT found: {imp_path}")
    
    logger.info(f"Total imports: {len(imports)}")
    
    # 6. Attempt lxml parsing (strict validation)
    logger.info(f"\n[Attempting lxml XSD compilation...]")
    try:
        xsd_doc = etree.parse(str(schema_path))
        xsd_schema = etree.XMLSchema(xsd_doc)
        logger.info(f"✓ lxml XSD compilation successful")
        return {
            "status": "SUCCESS",
            "xsd_compilable": True,
            "qname_issues_found": len(qname_issues),
            "namespaces": len(namespaces),
            "imports": len(imports)
        }
    except etree.XMLSchemaParseError as e:
        logger.error(f"✗ lxml XSD compilation failed (XMLSchemaParseError):")
        error_str = str(e)
        logger.error(f"   Error: {error_str[:300]}")
        logger.debug(f"   Full error: {error_str}")
        return {
            "status": "ERROR",
            "reason": "XSD compilation error",
            "detail": error_str[:500],
            "qname_issues_found": len(qname_issues),
            "error_type": "XMLSchemaParseError"
        }
    except Exception as e:
        logger.error(f"✗ Unexpected error during XSD compilation:")
        error_str = str(e)
        logger.error(f"   Error: {error_str[:300]}")
        logger.debug(f"   Full error: {error_str}")
        return {
            "status": "ERROR",
            "reason": "Unexpected error",
            "xsd_compilable": False,
            "lxml_error": error_str[:500],
            "qname_issues_found": len(qname_issues),
            "namespaces": len(namespaces),
            "imports": len(imports)
        }


def find_qname_issues(root, namespaces=None):
    """Find elements with unresolved QName references."""
    issues = []
    
    if namespaces is None:
        namespaces = extract_namespaces(root)
    
    # Search for substitutionGroup references
    for elem in root.iter():
        sg_attr = elem.get("substitutionGroup")
        if sg_attr:
            # Parse QName
            if ":" in sg_attr:
                prefix, local_name = sg_attr.split(":", 1)
            else:
                prefix = ""
                local_name = sg_attr
            
            # Try to resolve namespace
            if prefix:
                uri = namespaces.get(prefix)
                if not uri:
                    issues.append({
                        "element": elem.get("name", "unknown"),
                        "path": elem.tag,
                        "referenced_element": sg_attr,
                        "namespace": f"PREFIX '{prefix}' not found",
                        "severity": "ERROR"
                    })
            
            logger.debug(f"Found substitutionGroup: {sg_attr} on {elem.get('name')}")
    
    return issues


def extract_namespaces(root):
    """Extract all namespace declarations."""
    namespaces = {}
    if hasattr(root, 'nsmap'):
        for prefix, uri in root.nsmap.items():
            namespaces[prefix or "default"] = uri
    return namespaces


def find_schema_imports(root):
    """Find schema import/include directives."""
    imports = []
    for elem in root.iter():
        if elem.tag.endswith("}import") or elem.tag.endswith("}include"):
            location = elem.get("schemaLocation")
            if location:
                imports.append({
                    "type": "import" if elem.tag.endswith("}import") else "include",
                    "location": location,
                    "namespace": elem.get("namespace")
                })
    return imports


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s: %(message)s"
    )
    
    result = diagnose_xsd_schema("2023-1")
    print(f"\n{'='*70}")
    print(f"DIAGNOSTIC RESULT: {result['status']}")
    print(f"{'='*70}")
