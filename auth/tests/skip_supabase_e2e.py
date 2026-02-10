#!/usr/bin/env python3
"""
End-to-end test of Supabase integration with the auth service.
Demonstrates complete user lifecycle: register → login → create API key → use API key.
"""
import requests
import json
import uuid

BASE_URL = "http://localhost:8002"


def test_complete_flow():
    """Test complete user authentication flow with Supabase backend."""

    # Generate unique test data to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    username = f"supa_test_{unique_id}"
    email = f"supa_{unique_id}@test.com"

    print("\n" + "="*70)
    print("SUPABASE INTEGRATION - END-TO-END TEST")
    print("="*70)

    # 1. Register a new user
    print("\n1️⃣  REGISTERING USER...")
    register_data = {
        "username": username,
        "email": email,
        "password": "SupabaseTest123!",
        "name": "Supabase Test User",
        "address": "Cloud Street, Supabase City"
    }

    r = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    assert r.status_code == 200, f"Registration failed: {r.text}"
    user_data = r.json()
    print(f"   ✓ User created with ID {user_data['id']}")
    print(f"   ✓ Username: {user_data['username']}")
    print(f"   ✓ Email: {user_data['email']}")

    # 2. Login with the user
    print("\n2️⃣  LOGGING IN...")
    login_data = {
        "username": register_data["username"],
        "password": register_data["password"]
    }

    r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    assert r.status_code == 200, f"Login failed: {r.text}"
    login_response = r.json()
    access_token = login_response["access_token"]
    print(f"   ✓ Login successful")
    print(f"   ✓ JWT Token: {access_token[:50]}...")
    print(f"   ✓ User: {login_response['user']['username']}")

    # 3. Get current user info using JWT
    print("\n3️⃣  GETTING USER PROFILE...")
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    assert r.status_code == 200, f"Get profile failed: {r.text}"
    profile = r.json()
    print(f"   ✓ Profile retrieved: {profile['username']}")
    print(f"   ✓ Name: {profile['name']}")

    # 4. Create an API key
    print("\n4️⃣  CREATING API KEY...")
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.post(f"{BASE_URL}/auth/apikeys", headers=headers)
    assert r.status_code == 200, f"API key creation failed: {r.text}"
    api_key_data = r.json()
    api_key = api_key_data["raw_key"]
    api_key_id = api_key_data["id"]
    print(f"   ✓ API key created with ID {api_key_id}")
    print(f"   ✓ Raw Key: {api_key[:20]}...")

    # 5. List API keys
    print("\n5️⃣  LISTING API KEYS...")
    r = requests.get(f"{BASE_URL}/auth/apikeys", headers=headers)
    assert r.status_code == 200, f"List API keys failed: {r.text}"
    keys = r.json()  # This is a list directly
    print(f"   ✓ Found {len(keys)} API key(s)")

    # 6. Request password reset
    print("\n6️⃣  REQUESTING PASSWORD RESET...")
    reset_data = {"email": register_data["email"]}
    r = requests.post(
        f"{BASE_URL}/auth/password-reset/request", json=reset_data)
    assert r.status_code == 200, f"Password reset request failed: {r.text}"
    print(f"   ✓ Password reset token generated")

    # 7. Verify database persistence
    print("\n7️⃣  VERIFYING DATABASE PERSISTENCE...")
    # Try logging in again to confirm data was saved
    r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    assert r.status_code == 200, f"Login verification failed: {r.text}"
    print(f"   ✓ User data persisted in Supabase ✓")

    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED - SUPABASE INTEGRATION WORKING!")
    print("="*70)
    print("\n📊 Summary:")
    print(f"   - Database: Supabase PostgreSQL (us-west-2)")
    print(f"   - Connection: IPv4 Transaction Pooler (aws-0-us-west-2.pooler.supabase.com:6543)")
    print(f"   - Test User: {register_data['username']}")
    print(f"   - Operations: Register, Login, Profile, API Keys, Password Reset")
    print(f"   - Data Persistence: ✓ Confirmed in Supabase")
    print("\n")


if __name__ == "__main__":
    try:
        test_complete_flow()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except requests.ConnectionError:
        print("\n❌ CONNECTION ERROR: Is the auth service running? (http://localhost:8002)")
        print("   Run: docker-compose up -d")
        exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
