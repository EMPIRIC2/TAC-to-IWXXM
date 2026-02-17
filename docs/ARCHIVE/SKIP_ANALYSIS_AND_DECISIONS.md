# Test Skip Analysis & Decision Framework

## Current Status

### test_e2e_full_stack.py: 13 PASSED, 9 SKIPPED (41% skip rate)
Pattern: `...ss....ssss.s.....ss`

### test_dynamic_metar_generation.py: 178 PASSED, ~30+ SKIPPED (17% skip rate)  
Pattern: Multiple regional/phenomenon-based skips

---

## Root Causes of Skips

### A. test_e2e_full_stack.py (ENVIRONMENT-DEPENDENT SKIPS)

**Skip at Fixture Level (affects all dependent tests):**

1. **e2e_environment_check fixture** (Fixture Line 47, 52):
   - ✋ Skips if missing: `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`
   - ❌ **Impact**: Cascades to ~3 tests that use this fixture
   
2. **e2e_auth_token fixture** (Fixture Line 127):
   - ✋ Skips if missing: `E2E_TEST_EMAIL`, `E2E_TEST_PASSWORD`
   - ❌ **Impact**: Cascades to ALL tests using `e2e_auth_token` (~9 tests)

**Skip at Test Method Level (Line 441):**
3. **test_get_evaluation_job_results**: 
   - ✋ Skips if job creation failed (conditional logic)

### B. test_dynamic_metar_generation.py (DATA-AVAILABILITY SKIPS)

1. **test_regional_coverage_2023_1 / 2025_2** (7 parametrized tests):
   - ✋ Skips if `generator.regional_sample()` returns empty list
   - 🔍 **Root Cause**: No METAR data available for that region in current sample
   - Regions skipped: Likely `south_america`, `africa`, `middle_east` (less common in test data)

2. **test_phenomenon_conversion** (8 parametrized tests):
   - ✋ Skips if no examples found for phenomenon (RA, SN, TS, FG, BR, NSW, CB, TCU)
   - 🔍 **Root Cause**: Rare phenomena not in generated sample

3. **Main parametrized tests** (test_convert_to_iwxxm_2023_1/2025_2):
   - ✅ These DON'T skip - they catch exceptions and continue
   - Still seeing values because they're testing 200 METARs each

---

## Decision Options

### OPTION 1: ✨ Create Missing Environment Variables (Recommended for CI/CD)

**Cost**: 🔴 High - requires actual infrastructure  
**Benefit**: ✅ Run all E2E tests with real auth  
**Effort**: 1-2 hours setup

```bash
# Set up test credentials
export E2E_TEST_EMAIL="test-user@example.com"
export E2E_TEST_PASSWORD="secure_test_password_12345"
export DATABASE_URL="postgresql://user:pass@localhost:5432/metar_test"
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_ANON_KEY="your-anon-key"

# Then run
pytest backend/tests/test_e2e_full_stack.py -v -m e2e
```

**Pros:**
- Tests run with real database and auth
- Early detection of integration bugs
- Production-representative

**Cons:**
- Requires persistent test credentials
- Database cleanup complexity
- Supabase account dependency

---

### OPTION 2: 🚀 Make Environment Variables Optional (Recommended for local dev)

**Cost**: 🟢 Low - code change only  
**Benefit**: ✅ E2E tests still run with mocks  
**Effort**: 30 minutes

Create fixture decorators that mark tests as `skip_when_no_env` instead of hard-skipping:

```python
# Current behavior:
@pytest.fixture
def e2e_auth_token(e2e_environment_check):
    test_email = os.getenv("E2E_TEST_EMAIL")
    if not test_email:
        pytest.skip("E2E_TEST_EMAIL required")  # ❌ Skips entire test
    return token

# Better approach:
@pytest.fixture
def e2e_auth_token(e2e_environment_check):
    test_email = os.getenv("E2E_TEST_EMAIL")
    if not test_email:
        # Use mock token instead
        return "mock-test-token-" + uuid4()
    return token

# Or patch it at the test level:
@pytest.mark.parametrize("use_real_auth", [True, False])
def test_authenticated_flow(e2e_client, use_real_auth):
    if use_real_auth and not os.getenv("E2E_TEST_EMAIL"):
        pytest.skip("Real auth test")
    # ... test code
```

**Pros:**
- Tests run locally with mocks
- No external dependencies required
- Faster CI/CD execution
- Optional real auth when credentials available

**Cons:**
- Doesn't catch real auth bugs
- Mocks may hide integration issues

---

### OPTION 3: 📊 Split Test Scenarios (Hybrid Approach)

**Cost**: 🟡 Medium - requires test organization  
**Benefit**: ✅ Both mock and real tests available  
**Effort**: 1 hour refactoring

Structure tests by dependency level:

```
tests/
├── test_e2e_full_stack.py          # Mock-based (always runs)
│   ├── MockAuthenticationTests      # Uses mocked token ✅ 
│   └── RealAuthenticationTests      # Uses real Supabase ⚠️ (optional)
│
└── test_e2e_real_auth_only.py      # Real credentials only (optional)
    └── ProductionAuthTests         # Requires E2E vars
```

**Run modes:**
```bash
# Local development (always runs)
pytest backend/tests/test_e2e_full_stack.py -v

# Full CI/CD with real services (when vars present)
pytest backend/tests/test_e2e_*.py -v -m e2e
```

**Pros:**
- Flexibility: run with or without credentials
- Clear separation of concerns
- Scales to production testing

**Cons:**
- More test organization required
- Duplicate test logic

---

### OPTION 4: 🎭 Mark Tests with Conditional Skip Marker (Clean & Professional)

**Cost**: 🟢 Low - minimal code change  
**Benefit**: ✅ Clear visibility in reports  
**Effort**: 45 minutes

Use pytest custom marker:

```python
# conftest.py
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "requires_auth: test requires E2E credentials"
    )

# test_e2e_full_stack.py
@pytest.mark.requires_auth
def test_authenticated_conversion(e2e_client, e2e_auth_token):
    # Only runs if E2E_TEST_EMAIL is set
    pass
```

Then run:
```bash
# Skip auth tests (local dev)
pytest -m "not requires_auth"

# Only auth tests (CI with credentials)
pytest -m "requires_auth"

# All tests (full suite)
pytest
```

**Pros:**
- Explicit test categorization
- Flexible filtering
- Clean CLI usage
- Professional reporting

**Cons:**
- Tests still skip, just more visible

---

### OPTION 5: ⚙️ Use conftest.py to Auto-Mock Missing Vars (Smart & Automatic)

**Cost**: 🟡 Medium - conftest logic required  
**Benefit**: ✅ Automatic fallback to mocks  
**Effort**: 45 minutes

```python
# backend/conftest.py
@pytest.fixture(autouse=True)
def auto_mock_e2e_vars(monkeypatch):
    """Automatically mock missing E2E variables."""
    
    # If no test credentials, use fake ones
    if not os.getenv("E2E_TEST_EMAIL"):
        monkeypatch.setenv("E2E_TEST_EMAIL", "auto-mock@test.local")
        monkeypatch.setenv("E2E_TEST_PASSWORD", "auto-mock-pwd")
    
    # If no database, use test database
    if not os.getenv("DATABASE_URL"):
        monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

# Now fixtures never skip - they use defaults
@pytest.fixture
def e2e_auth_token(e2e_environment_check):
    test_email = os.getenv("E2E_TEST_EMAIL")  # Always has value
    test_password = os.getenv("E2E_TEST_PASSWORD")  # Always has value
    # ... proceed without skip
```

**Pros:**
- Tests never skip
- Fallback mocks are automatic
- Real credentials override mocks
- No test code changes needed

**Cons:**
- Less explicit about what's mocked
- May hide credential issues

---

### OPTION 6: 📈 Improve test_dynamic_metar_generation.py Regional Coverage

**For the ~30 dynamic test skips:**

**Current Issue**: Regional skips happen when `generator.regional_sample()` returns empty list

**Solutions:**

```python
# A) Expand sample size
def test_regional_coverage_2023_1(self, region: str):
    regional_cases = generator.regional_sample(region, count=50, hours=24)  # Increase from 20
    # More data = better chance of coverage

# B) Add timeout/skip message tracking
if len(regional_cases) == 0:
    pytest.skip(f"No {region} METARs in sample (check aviation-weather service)")

# C) Pre-warm the METAR cache
@pytest.fixture(scope="session", autouse=True)
def preload_metar_cache():
    generator.force_refresh_all_regions()  # Load 24h of data upfront

# D) Make test less strict
if len(regional_cases) > 0:
    success_rate = success_count / len(regional_cases)
    assert success_rate >= 0.3, ...  # Reduce from 50% to 30%
```

---

## Recommendation Framework

Choose based on your situation:

| Scenario | Recommendation | Why |
|----------|---------------|-----|
| **Local development** | Option 2 (Mock optional) | No setup needed, instant feedback |
| **CI/CD with credentials available** | Option 1 (Use env vars) | Tests real integration |
| **CI/CD mixed mode (sometimes real)** | Option 3 (Split by marker) | Flexibility without duplication |
| **Production monitoring** | Option 1 + Option 3 | Tests both mock and real |
| **Team collaboration** | Option 5 (Auto-mock) | Works for everyone, configurable |
| **Clear reporting** | Option 4 (Custom markers) + Option 2 | Visible in pytest output |

---

## Implementation Priority

1. **Immediate** (5 min): Run with `-m "not requires_auth"` to see non-auth tests
2. **Short-term** (30 min): Add Option 5 auto-mocking logic to conftest.py
3. **Medium-term** (1 hr): Implement Option 4 markers for clean categorization
4. **Long-term** (2+ hrs): Add real E2E credentials to CI/CD (Option 1)

---

## Quick Tests to Validate

```bash
# Test with current setup (expect skips)
pytest backend/tests/test_e2e_full_stack.py -v --tb=no

# Test without auth-dependent tests
pytest backend/tests/test_e2e_full_stack.py -v -k "not token and not authenticated"

# Dynamic tests with verbosity
pytest backend/tests/test_dynamic_metar_generation.py -v -s
```

