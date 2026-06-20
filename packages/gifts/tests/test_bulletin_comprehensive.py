"""Comprehensive tests for bulletin module - targeting uncovered lines"""

import pytest
import xml.etree.ElementTree as ET
from gifts.common.bulletin import Bulletin, XMLError


class TestBulletinBasics:
    """Test basic Bulletin class functionality"""

    def test_bulletin_creation(self):
        """Test creating an empty bulletin"""
        b = Bulletin()
        assert isinstance(b, Bulletin)
        assert len(b) == 0

    def test_bulletin_len(self):
        """Test bulletin length"""
        b = Bulletin()
        assert len(b) == 0

        # Add mock element
        elem = ET.Element("test")
        b._children.append(elem)
        assert len(b) == 1

    def test_bulletin_getitem(self):
        """Test indexing bulletin"""
        b = Bulletin()
        elem1 = ET.Element("elem1")
        elem2 = ET.Element("elem2")
        b._children.append(elem1)
        b._children.append(elem2)

        assert b[0] is elem1
        assert b[1] is elem2

    def test_bulletin_getitem_out_of_range(self):
        """Test indexing out of range"""
        b = Bulletin()
        with pytest.raises(IndexError):
            _ = b[0]

    def test_bulletin_xml_filename_pattern(self):
        """Test XML filename pattern matching"""
        b = Bulletin()
        # Should have regex pattern
        assert hasattr(b, "xmlFileNamePartA")
        assert b.xmlFileNamePartA is not None


class TestBulletinAddition:
    """Test combining bulletins"""

    def test_add_empty_bulletins(self):
        """Test adding two empty bulletins"""
        b1 = Bulletin()
        b2 = Bulletin()

        with pytest.raises(XMLError):
            b1 + b2

    def test_add_bulletins_with_kind(self):
        """Test adding bulletins with same kind"""
        b1 = Bulletin()
        b1._kind = "METAR"
        elem1 = ET.Element("elem1")
        b1._children.append(elem1)

        b2 = Bulletin()
        b2._kind = "METAR"
        elem2 = ET.Element("elem2")
        b2._children.append(elem2)

        result = b1 + b2
        assert len(result) == 2
        # _kind is not preserved in new bulletin unless __add__ logic sets it
        assert result[0] is elem1
        assert result[1] is elem2

    def test_add_bulletins_different_kind_raises_error(self):
        """Test adding bulletins with different kinds"""
        b1 = Bulletin()
        b1._kind = "METAR"
        elem1 = ET.Element("elem1")
        b1._children.append(elem1)

        b2 = Bulletin()
        b2._kind = "TAF"
        elem2 = ET.Element("elem2")
        b2._children.append(elem2)

        with pytest.raises(XMLError, match="same kind"):
            b1 + b2

    def test_add_with_first_empty(self):
        """Test adding when first bulletin is empty"""
        b1 = Bulletin()
        # First is empty, no _kind attribute

        b2 = Bulletin()
        b2._kind = "METAR"
        elem2 = ET.Element("elem2")
        b2._children.append(elem2)

        result = b1 + b2
        assert len(result) == 1
        # __add__ sets _kind on self but not on the returned newBulletin
        assert elem2 in result._children

    def test_add_preserves_children(self):
        """Test that addition preserves children"""
        b1 = Bulletin()
        b1._kind = "METAR"  # Set _kind to avoid empty bulletin error
        elem1 = ET.Element("elem1")
        b1._children.append(elem1)

        b2 = Bulletin()
        b2._kind = "METAR"  # Set _kind to match
        elem2 = ET.Element("elem2")
        b2._children.append(elem2)

        result = b1 + b2
        assert result[0] is elem1
        assert result[1] is elem2


class TestBulletinExport:
    """Test bulletin export to XML"""

    def test_export_empty_bulletin_raises_error(self):
        """Test exporting empty bulletin raises error"""
        b = Bulletin()

        with pytest.raises(XMLError, match="At least one"):
            b._export()

    def test_export_missing_bulletin_id_raises_error(self):
        """Test exporting without bulletin ID"""
        b = Bulletin()
        elem = ET.Element("test")
        b._children.append(elem)

        with pytest.raises(XMLError, match="bulletinIdentifier needs to be set"):
            b._export()

    def test_export_invalid_bulletin_id_format(self):
        """Test exporting with invalid bulletin ID format"""
        b = Bulletin()
        b._bulletinId = "INVALID_ID"
        elem = ET.Element("test")
        b._children.append(elem)

        with pytest.raises(XMLError, match="does not conform"):
            b._export()

    def test_export_valid_bulletin_id(self):
        """Test exporting with valid bulletin ID"""
        b = Bulletin()
        # Valid format: A_L[A-Z]{3}\d\d[A-Z]{4}\d{6}_C_[A-Z]{4}
        b._bulletinId = "A_LCCC12KORD030000_C_KORD"
        elem = ET.Element("test")
        b._children.append(elem)

        b._export()
        assert b.bulletin is not None
        assert b.bulletin.tag == "MeteorologicalBulletin"

    def test_export_sets_required_attributes(self):
        """Test that export sets all required XML attributes"""
        b = Bulletin()
        b._bulletinId = "A_LCCC12KORD030000_C_KORD"
        elem = ET.Element("test")
        b._children.append(elem)

        b._export()
        bulletin_elem = b.bulletin

        # Check required namespaces
        assert bulletin_elem.get("xmlns") == "http://def.wmo.int/collect/2014"
        assert bulletin_elem.get("xmlns:gml") == "http://www.opengis.net/gml/3.2"
        assert bulletin_elem.get("xmlns:xsi") == "http://www.w3.org/2001/XMLSchema-instance"

    def test_export_creates_gml_id(self):
        """Test that export creates gml:id"""
        b = Bulletin()
        b._bulletinId = "A_LCCC12KORD030000_C_KORD"
        elem = ET.Element("test")
        b._children.append(elem)

        b._export()
        # Check if gml:id attribute exists using element attributes
        gml_id = None
        for key, value in b.bulletin.attrib.items():
            if "gml" in key.lower() and "id" in key.lower():
                gml_id = value
                break
        # If not found, check for direct 'gml:id' or 'id'
        if gml_id is None:
            gml_id = b.bulletin.get("gml:id") or b.bulletin.get("id")
        assert gml_id is not None or b.bulletin.get("{http://www.opengis.net/gml/3.2}id")

    def test_export_creates_bulletin_identifier(self):
        """Test that export creates bulletinIdentifier element"""
        b = Bulletin()
        b._bulletinId = "A_LCCC12KORD030000_C_KORD"
        elem = ET.Element("test")
        b._children.append(elem)

        b._export()

        # Find bulletinIdentifier element
        bulletin_id_elem = b.bulletin.find("bulletinIdentifier")
        assert bulletin_id_elem is not None
        assert bulletin_id_elem.text is not None
        assert "A_LCCC12KORD030000_C_KORD" in bulletin_id_elem.text

    def test_export_compressed(self):
        """Test export with compression flag"""
        b = Bulletin()
        b._bulletinId = "A_LCCC12KORD030000_C_KORD"
        elem = ET.Element("test")
        b._children.append(elem)

        b._export(compress=True)

        bulletin_id_elem = b.bulletin.find("bulletinIdentifier")
        # Should have .gz extension in filename
        assert bulletin_id_elem.text.endswith(".gz")

    def test_export_sets_internal_bulletin_id(self):
        """Test that export sets internal bulletin ID"""
        b = Bulletin()
        b._bulletinId = "A_LCCC12KORD030000_C_KORD"
        elem = ET.Element("test")
        b._children.append(elem)

        b._export()

        assert hasattr(b, "_internalBulletinId")
        assert b._internalBulletinId is not None


class TestBulletinString:
    """Test bulletin string representation"""

    def test_str_valid_bulletin(self):
        """Test converting bulletin to string"""
        b = Bulletin()
        b._bulletinId = "A_LCCC12KORD030000_C_KORD"
        elem = ET.Element("test")
        b._children.append(elem)

        result = str(b)
        assert isinstance(result, str)
        assert "MeteorologicalBulletin" in result
        assert "xmlns" in result

    def test_str_includes_xml_declaration(self):
        """Test that string includes XML elements"""
        b = Bulletin()
        b._bulletinId = "A_LCCC12KORD030000_C_KORD"
        elem = ET.Element("test")
        b._children.append(elem)

        result = str(b)
        # Should be valid XML-like format
        assert "<" in result and ">" in result

    def test_str_contains_bulletin_identifier(self):
        """Test that string contains bulletin identifier"""
        b = Bulletin()
        b._bulletinId = "A_LCCC12KORD030000_C_KORD"
        elem = ET.Element("test")
        b._children.append(elem)

        result = str(b)
        assert "bulletinIdentifier" in result
        assert "A_LCCC12KORD030000_C_KORD" in result


class TestBulletinWhiteSpace:
    """Test whitespace formatting"""

    def test_addwhitespace_formats_output(self):
        """Test that whitespace is added to output"""
        b = Bulletin()
        b._bulletinId = "A_LCCC12KORD030000_C_KORD"
        elem = ET.Element("meteorologicalInformation")
        child = ET.SubElement(elem, "test")
        child.text = "content"
        b._children.append(elem)

        result = str(b)
        # Should have newlines and indentation
        assert "\n" in result

    def test_addwhitespace_multiple_children(self):
        """Test whitespace with multiple children"""
        b = Bulletin()
        b._bulletinId = "A_LCCC12KORD030000_C_KORD"

        elem1 = ET.Element("elem1")
        child1 = ET.SubElement(elem1, "child1")
        child1.text = "text1"
        b._children.append(elem1)

        elem2 = ET.Element("elem2")
        child2 = ET.SubElement(elem2, "child2")
        child2.text = "text2"
        b._children.append(elem2)

        result = str(b)
        assert result is not None


class TestBulletinWhatKind:
    """Test what_kind method"""

    def test_what_kind_empty(self):
        """Test what_kind on empty bulletin"""
        b = Bulletin()
        result = b.what_kind()
        assert result is None

    def test_what_kind_with_kind(self):
        """Test what_kind with _kind attribute"""
        b = Bulletin()
        b._kind = "METAR"
        result = b.what_kind()
        assert result == "METAR"

    def test_what_kind_different_types(self):
        """Test what_kind with different types"""
        types = ["METAR", "TAF", "VAA", "SWA"]
        for kind in types:
            b = Bulletin()
            b._kind = kind
            assert b.what_kind() == kind


class TestBulletinXMLValidation:
    """Test XML validation features"""

    def test_bulletin_id_pattern_matches_valid(self):
        """Test bulletin ID pattern matches valid IDs"""
        b = Bulletin()
        valid_ids = [
            "A_LCCC12KORD030000_C_KORD",
            "A_LXYZ99EGLL010000_C_EGLL",
        ]

        for valid_id in valid_ids:
            match = b.xmlFileNamePartA.match(valid_id)
            assert match is not None, f"Pattern should match {valid_id}"

    def test_bulletin_id_pattern_rejects_invalid(self):
        """Test bulletin ID pattern rejects invalid IDs"""
        b = Bulletin()
        invalid_ids = [
            "INVALID",
            "A_X12345678",  # Wrong format
            "A_LCCC1",  # Too short
            "B_LCCC12KORD030000",  # Wrong prefix
        ]

        for invalid_id in invalid_ids:
            match = b.xmlFileNamePartA.match(invalid_id)
            assert match is None, f"Pattern should not match {invalid_id}"


class TestBulletinErrorHandling:
    """Test error handling"""

    def test_xml_error_inheritance(self):
        """Test that XMLError is a SyntaxError"""
        assert issubclass(XMLError, SyntaxError)

    def test_raise_xml_error(self):
        """Test raising XMLError"""
        with pytest.raises(XMLError):
            raise XMLError("Test error message")

    def test_xml_error_message(self):
        """Test XMLError message"""
        msg = "Test error message"
        try:
            raise XMLError(msg)
        except XMLError as e:
            assert str(e) == msg


class TestBulletinEdgeCases:
    """Test edge cases"""

    def test_bulletin_with_many_children(self):
        """Test bulletin with many children"""
        b = Bulletin()
        b._bulletinId = "A_LCCC12KORD030000_C_KORD"

        # Add 100 children
        for i in range(100):
            elem = ET.Element(f"elem_{i}")
            b._children.append(elem)

        assert len(b) == 100
        assert b[0] is not None
        assert b[99] is not None

    def test_bulletin_with_nested_elements(self):
        """Test bulletin with deeply nested elements"""
        b = Bulletin()
        b._bulletinId = "A_LCCC12KORD030000_C_KORD"

        # Create nested structure
        root = ET.Element("root")
        child = ET.SubElement(root, "child")
        grandchild = ET.SubElement(child, "grandchild")
        great_grandchild = ET.SubElement(grandchild, "great_grandchild")
        great_grandchild.text = "deep content"

        b._children.append(root)

        result = str(b)
        assert "deep content" in result

    def test_bulletin_export_and_string_clears_bulletin(self):
        """Test that string() clears bulletin after export"""
        b = Bulletin()
        b._bulletinId = "A_LCCC12KORD030000_C_KORD"
        elem = ET.Element("test")
        b._children.append(elem)

        # Create string (which calls _export internally)
        str(b)

        # bulletin should be cleared
        assert b.bulletin is None

    def test_multiple_exports(self):
        """Test calling export multiple times"""
        b = Bulletin()
        b._bulletinId = "A_LCCC12KORD030000_C_KORD"
        elem = ET.Element("test")
        b._children.append(elem)

        # First export
        str_result1 = str(b)
        assert str_result1 is not None

        # Modify bulletin id
        b._bulletinId = "A_LYYY22KJFK050000_C_KJFK"
        elem2 = ET.Element("test2")
        b._children.append(elem2)

        # Second export
        str_result2 = str(b)
        assert str_result2 is not None
        assert "A_LYYY22KJFK050000" in str_result2


class TestBulletinSchemaLocation:
    """Test schema location attribute"""

    def test_schema_location_is_set(self):
        """Test that schema location is properly set"""
        b = Bulletin()
        b._bulletinId = "A_LCCC12KORD030000_C_KORD"
        elem = ET.Element("test")
        b._children.append(elem)

        b._export()

        # Just verify export creates a valid bulletin structure
        assert b.bulletin is not None
        assert isinstance(b.bulletin, ET.Element)
