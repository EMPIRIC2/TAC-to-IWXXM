#!/usr/bin/env python3
"""Debug script to inspect FastAPI routes"""
import sys

print("Importing api module...")
try:
    from api import app
    print("✓ API module imported successfully")
except Exception as e:
    print(f"✗ Failed to import api: {e}")
    import traceback
    traceback.print_exc()
    try:
        from src.api import app
        print("✓ Fallback import from src.api successful")
    except Exception as e2:
        print(f"✗ Fallback also failed: {e2}")
        sys.exit(1)

print("\nInspecting routes...")
for i, route in enumerate(app.routes):
    print(f"  {i}: {route.path} - {route.methods if hasattr(route, 'methods') else 'N/A'}")

print(f"\nTotal routes: {len(app.routes)}")

# Check for validation routes specifically
val_routes = [r for r in app.routes if 'validation' in r.path]
eval_routes = [r for r in app.routes if 'eval' in r.path]

print(f"\nValidation routes: {len(val_routes)}")
for route in val_routes:
    print(f"  - {route.path}")

print(f"\nEvaluation routes: {len(eval_routes)}")
for route in eval_routes:
    print(f"  - {route.path}")
