#!/usr/bin/env python3
"""
Direct admin approval via Supabase Management API
Bypasses transaction pooler and uses service role key
"""
import os
import sys
import json
import subprocess
from pathlib import Path

# Load environment
env_file = Path(__file__).parent.parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value.strip('"\'')

SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
ADMIN_USER_ID = '27f7a37c-5575-4e19-a6d6-338755caec1d'

if not SUPABASE_URL or not SERVICE_ROLE_KEY:
    print("❌ Missing VITE_SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")
    sys.exit(1)

# Extract project ID from URL
project_id = SUPABASE_URL.split('//')[1].split('.')[0]
rest_url = f"{SUPABASE_URL}/rest/v1"

print(f"🔍 Attempting direct API update...")
print(f"Project: {project_id}")
print(f"User ID: {ADMIN_USER_ID}")

# Attempt 1: Direct REST API PATCH
print("\n📡 Attempt 1: REST API PATCH (with Authorization header)")
cmd = [
    'curl', '-X', 'PATCH',
    f'{rest_url}/user_profiles?id=eq.{ADMIN_USER_ID}',
    '-H', 'Content-Type: application/json',
    '-H', f'Authorization: Bearer {SERVICE_ROLE_KEY}',
    '-H', 'Prefer: return=representation',
    '-d', json.dumps({
        'is_admin': True,
        'approval_status': 'approved'
    })
]

result = subprocess.run(cmd, capture_output=True, text=True)
print(f"Status: {result.returncode}")
if result.stdout:
    print(f"Response: {result.stdout}")
if result.stderr:
    print(f"Error: {result.stderr}")

# Verify the update
print("\n✅ Verification: Checking current values...")
cmd = [
    'curl', '-s',
    f'{rest_url}/user_profiles?id=eq.{ADMIN_USER_ID}&select=id,email,username,is_admin,approval_status',
    '-H', f'Authorization: Bearer {SERVICE_ROLE_KEY}'
]

result = subprocess.run(cmd, capture_output=True, text=True)
if result.stdout:
    try:
        data = json.loads(result.stdout)
        if data and len(data) > 0:
            profile = data[0]
            print(f"\n📋 Current Profile:")
            print(f"  Email: {profile.get('email')}")
            print(f"  Username: {profile.get('username')}")
            print(f"  is_admin: {profile.get('is_admin')} {'✅' if profile.get('is_admin') else '❌'}")
            print(f"  approval_status: {profile.get('approval_status')} {'✅' if profile.get('approval_status') == 'approved' else '❌'}")
        else:
            print("❌ User profile not found")
    except json.JSONDecodeError:
        print(f"Response: {result.stdout}")
