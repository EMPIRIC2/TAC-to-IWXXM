#!/usr/bin/env python3
"""Quick test of the API endpoint with new validation features."""

import requests


def test_api_with_validation():
    """Test the API endpoint with validation enabled."""

    # Start with a test that should pass
    print("=== Testing API with Valid METAR ===")

    valid_metar = "METAR VTUO 290000Z 22003KT 190V360 2000 BR FEW035 25/25 Q1011 BECMG FM0100 3000 BR="

    data = {
        "manual_text": valid_metar,
        "iwxxm_version": "2025-2",
        "validate_output": "false",  # Start without output validation for speed
    }

    try:
        response = requests.post(
            "http://localhost:8002/api/v1/convert",
            data=data,
            headers={"Authorization": "Bearer dummy"},  # DISABLE_AUTH should be set
        )

        if response.status_code == 200:
            result = response.json()
            print("✓ Conversion successful")
            print(f"  Total processed: {result['total_processed']}")
            print(f"  Successful: {result['successful']}")
            print(f"  Failed: {result['failed']}")

            if result["results"]:
                xml = result["results"][0]["content"]
                if "BURI RAM AIRPORT" in xml:
                    print("  ✓ Airport name capitalized correctly")
                else:
                    print("  ✗ Airport name not capitalized")

                if xml.startswith("<?xml version"):
                    print("  ✓ XML declaration present")
                else:
                    print("  ✗ XML declaration missing")
        else:
            print(f"✗ Request failed with status {response.status_code}")
            print(f"  Response: {response.text[:200]}")

    except requests.exceptions.ConnectionError:
        print("⚠ Server not running on localhost:8002")
        print("  To test manually, start the server with:")
        print(
            "  cd /root/metar-to-IWXXM/backend && DISABLE_AUTH=true uv run uvicorn src.api:app --host 0.0.0.0 --port 8002 --reload"
        )
        return
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Test with invalid METAR (should be caught by validation)
    print("\n=== Testing API with Invalid METAR (No ICAO) ===")

    invalid_metar = "290000Z 22003KT 190V360 2000 BR FEW035 25/25 Q1011"

    data = {
        "manual_text": invalid_metar,
        "iwxxm_version": "2025-2",
    }

    try:
        response = requests.post(
            "http://localhost:8002/api/v1/convert", data=data, headers={"Authorization": "Bearer dummy"}
        )

        if response.status_code == 400:
            print("✓ Invalid METAR correctly rejected")
            result = response.json()
            if "detail" in result:
                print(f"  Error details: {result['detail']}")
        elif response.status_code == 200:
            result = response.json()
            if result.get("failed", 0) > 0:
                print("✓ Invalid METAR caught during processing")
                print(f"  Errors: {result.get('errors', [])}")
            else:
                print("✗ Invalid METAR was not caught")
        else:
            print(f"? Unexpected status: {response.status_code}")

    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    test_api_with_validation()
