#!/usr/bin/env python3
"""
Test login directly to make sure the endpoint works
"""

import requests
import json

print("Testing direct login to auth service...")
print("=" * 60)

url = "http://localhost:8002/auth/login"

# Test with admin credentials
payload = {"email": "admin@metar.local", "password": "Admin123456!"}

print(f"\n1. POST {url}")
print(f"   Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(
        url, json=payload, headers={"Content-Type": "application/json", "Origin": "http://localhost:8000"}, timeout=10
    )

    print(f"\n   Status: {response.status_code}")
    print(f"   Headers:")
    for key, value in response.headers.items():
        if "access-control" in key.lower() or "content-type" in key.lower():
            print(f"     {key}: {value}")

    print(f"\n   Body:")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)

    if response.status_code == 200:
        print("\n✓ Login successful!")
    else:
        print(f"\n✗ Login failed with status {response.status_code}")

except requests.exceptions.ConnectionError as e:
    print(f"\n✗ Connection error: {e}")
    print("   Is the auth service running?")
except requests.exceptions.Timeout:
    print(f"\n✗ Request timed out")
except Exception as e:
    print(f"\n✗ Error: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
