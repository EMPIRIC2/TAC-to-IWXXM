#!/usr/bin/env python3
"""
Quick test to check if auth service is reachable
"""
import requests
import time

print("Testing auth service connectivity...")
print("=" * 60)

auth_url = "http://localhost:8002"

# Test 1: Health check
print("\n[Test 1] Health check endpoint")
try:
    response = requests.get(f"{auth_url}/health", timeout=5)
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Response: {response.json()}")
except requests.exceptions.ConnectionError:
    print("✗ Connection refused - Auth service not running?")
    print("  Start it with: cd auth && uv run uvicorn src.__main__:app --reload --port 8002")
    exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

# Test 2: CORS preflight (OPTIONS)
print("\n[Test 2] CORS preflight (OPTIONS) to /auth/login")
try:
    response = requests.options(
        f"{auth_url}/auth/login",
        headers={
            "Origin": "http://localhost:8000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        },
        timeout=5
    )
    print(f"✓ Status: {response.status_code}")
    print(f"✓ CORS Headers:")
    cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
    for key, value in cors_headers.items():
        print(f"    {key}: {value}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: POST to login (should fail with 401 or validation error)
print("\n[Test 3] POST to /auth/login (empty body - should get validation error)")
try:
    response = requests.post(
        f"{auth_url}/auth/login",
        json={"email": "test@test.com", "password": "wrongpassword"},
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    print(f"✓ Status: {response.status_code}")
    if response.status_code >= 400:
        print(f"✓ Error response (expected): {response.json()}")
    else:
        print(f"Response: {response.json()}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("✓ Auth service is reachable and responding!")
print("=" * 60)
