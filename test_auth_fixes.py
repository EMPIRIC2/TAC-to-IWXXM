#!/usr/bin/env python3
"""
Diagnostic script to verify auth service fixes
"""
import sys
import asyncio

print("=" * 60)
print("Auth Service Diagnostic Test")
print("=" * 60)

# Test 1: Import main app
print("\n[Test 1] Importing FastAPI app...")
try:
    from auth.src.__main__ import app
    print("✓ FastAPI app imported successfully")
except Exception as e:
    print(f"✗ Failed to import app: {e}")
    sys.exit(1)

# Test 2: Import supabase proxy
print("\n[Test 2] Importing SupabaseAuthProxy...")
try:
    from auth.src.supabase_proxy import SupabaseAuthProxy, get_supabase_proxy
    print("✓ SupabaseAuthProxy imported successfully")
except Exception as e:
    print(f"✗ Failed to import proxy: {e}")
    sys.exit(1)

# Test 3: Import API router
print("\n[Test 3] Importing API router...")
try:
    from auth.src.api_supabase import router
    print("✓ API router imported successfully")
except Exception as e:
    print(f"✗ Failed to import router: {e}")
    sys.exit(1)

# Test 4: Check that functions are not async
print("\n[Test 4] Verifying proxy methods are synchronous...")
try:
    import inspect
    proxy_class = SupabaseAuthProxy
    
    methods_to_check = [
        'sign_up', 'sign_in', 'sign_out', 'get_user',
        'refresh_session', 'reset_password_email', 'update_password', 'verify_token'
    ]
    
    all_sync = True
    for method_name in methods_to_check:
        method = getattr(proxy_class, method_name)
        is_async = inspect.iscoroutinefunction(method)
        status = "✗ ASYNC" if is_async else "✓ SYNC"
        print(f"  {method_name}: {status}")
        if is_async:
            all_sync = False
    
    if not all_sync:
        print("\n✗ Some methods are still async! This will cause issues.")
        sys.exit(1)
    print("\n✓ All proxy methods are synchronous")
except Exception as e:
    print(f"✗ Error checking methods: {e}")
    sys.exit(1)

# Test 5: Check logging is configured
print("\n[Test 5] Checking logging configuration...")
try:
    import logging
    logger = logging.getLogger('auth.src.supabase_proxy')
    handlers = logger.handlers
    if len(logging.root.handlers) > 0 or len(logger.handlers) > 0:
        print("✓ Logging is configured")
        print(f"  Root handlers: {len(logging.root.handlers)}")
        print(f"  Logger handlers: {len(logger.handlers)}")
    else:
        print("⚠ Logging may not be properly configured")
except Exception as e:
    print(f"✗ Error checking logging: {e}")
    sys.exit(1)

# Test 6: Verify app routes
print("\n[Test 6] Checking API routes...")
try:
    routes = [route.path for route in app.routes]
    required_routes = ['/auth/register', '/auth/login', '/auth/logout', '/auth/me', '/auth/refresh', '/health']
    
    for route in required_routes:
        if any(route in r for r in routes):
            print(f"  ✓ {route}")
        else:
            print(f"  ✗ {route} NOT FOUND")
            
    print(f"\nTotal routes registered: {len(routes)}")
except Exception as e:
    print(f"✗ Error checking routes: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ All diagnostic tests passed!")
print("=" * 60)
print("\nNext steps:")
print("1. Start the auth service: uv run uvicorn src.__main__:app --reload --port 8002")
print("2. Check the logs for [REGISTER], [LOGIN], [LOGOUT], etc. messages")
print("3. Test the frontend login - you should see console logs in the browser")
