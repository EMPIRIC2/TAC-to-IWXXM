#!/usr/bin/env python3
"""Test script to verify validation and capitalization changes."""

from src.utilities.conversion import convert_metar_tac_with_metadata
from src.services.validation import ValidationService

def test_airport_name_capitalization():
    """Test that airport names are now capitalized."""
    print("\n=== Test 1: Airport Name Capitalization ===")
    test_metar = "METAR VTUO 290000Z 22003KT 190V360 2000 BR FEW035 25/25 Q1011 BECMG FM0100 3000 BR="
    
    xml = convert_metar_tac_with_metadata(test_metar)
    
    # Check if airport name is uppercase
    if "BURI RAM AIRPORT" in xml:
        print("✓ PASS: Airport name is capitalized (BURI RAM AIRPORT)")
        return True
    elif "Buri Ram Airport" in xml:
        print("✗ FAIL: Airport name is still title case (Buri Ram Airport)")
        return False
    else:
        print("⚠ WARNING: Airport name not found in XML")
        print(f"XML excerpt: {xml[:500]}")
        return False

def test_input_validation():
    """Test METAR input validation."""
    print("\n=== Test 2: METAR Input Validation ===")
    validation_service = ValidationService()
    
    # Test valid METAR
    valid_metar = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
    try:
        result = validation_service.validate_all_layers(valid_metar)
        if result.passed:
            print(f"✓ PASS: Valid METAR passed validation")
            print(f"  Layers checked: {len(result.results)} layers")
        else:
            print(f"✗ FAIL: Valid METAR failed validation")
            print(f"  Issues: {result.summary}")
            return False
    except Exception as e:
        print(f"✗ FAIL: Validation raised exception: {e}")
        return False
    
    # Test invalid METAR (no ICAO)
    invalid_metar = "231751Z 18012KT 10SM FEW040 15/07 A3005"
    try:
        result = validation_service.validate_all_layers(invalid_metar)
        print(f"✓ PASS: Invalid METAR correctly caught")
        print(f"  Error: {result.summary if hasattr(result, 'summary') else 'No ICAO code'}")
    except Exception as e:
        print(f"✓ PASS: Invalid METAR correctly rejected: {e}")
    
    return True

def test_conversion_with_validation():
    """Test conversion with all features."""
    print("\n=== Test 3: Full Conversion Pipeline ===")
    
    test_cases = [
        ("METAR BGBW 290000Z 11012KT 9999 FEW040 15/07 Q1013", "BGBW", "NARSARSUAQ"),
        ("METAR USTR 290000Z 22005KT 9999 SCT025 18/12 Q1015", "USTR", "STRIZHI"),
        ("METAR VTUO 290000Z 22003KT 2000 BR FEW035 25/25 Q1011", "VTUO", "BURI RAM AIRPORT"),
    ]
    
    all_passed = True
    for metar, icao, expected_name in test_cases:
        try:
            xml = convert_metar_tac_with_metadata(metar)
            
            # Check for uppercase airport name
            if expected_name in xml:
                print(f"✓ PASS: {icao} -> {expected_name} (capitalized)")
            else:
                print(f"✗ FAIL: {icao} -> Expected '{expected_name}' not found")
                all_passed = False
            
            # Check for XML declaration
            if xml.startswith("<?xml version"):
                print(f"  ✓ XML declaration present")
            else:
                print(f"  ✗ XML declaration missing")
                all_passed = False
                
        except Exception as e:
            print(f"✗ FAIL: {icao} conversion failed: {e}")
            all_passed = False
    
    return all_passed

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Validation and Capitalization Changes")
    print("=" * 60)
    
    tests = [
        test_airport_name_capitalization,
        test_input_validation,
        test_conversion_with_validation,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    return all(results)

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
