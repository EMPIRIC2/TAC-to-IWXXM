# CI/CD Pipeline - 95% Test Coverage Requirement

## Overview

This CI/CD pipeline enforces **95% minimum test coverage** across all projects in the METAR to IWXXM repository:

- ✅ **Backend** (Python, pytest)
- ✅ **Auth Service** (Python, pytest)
- ✅ **GIFTs** (Python, pytest)
- ✅ **Frontend** (TypeScript/JavaScript, Vitest)

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ GitHub Push (main/dev) or Pull Request                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │   Backend    │  │   Auth Svc   │  │   GIFTs      │
  │   95% Req    │  │   95% Req    │  │   95% Req    │
  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
         │                  │                 │
         └──────────────────┼─────────────────┘
                            │
        ┌───────────────────┴──────────────────┐
        │                                      │
        ▼                                      ▼
  ┌──────────────┐                    ┌──────────────┐
  │   Frontend   │                    │ Coverage     │
  │   95% Req    │                    │ Enforcement  │
  └──────┬───────┘                    └──────┬───────┘
         │                                    │
         └────────────────┬───────────────────┘
                          │
                    ✅ All pass?
                          │
        ┌─────────────────┴──────────────────┐
        │                                    │
       YES                                   NO
        │                                    │
        ▼                                    ▼
  Build & Push                          ❌ FAIL
  Docker Images                         Build Blocks
```

## Jobs & Requirements

### 1. Backend Tests (`backend-tests`)
**Trigger:** Running on Ubuntu latest with Python 3.11

```bash
cd backend
uv pip install -e ".[dev]" skyfield httpx
python -m pytest tests/ --cov=src --cov-fail-under=95
```

**Requirements:**
- ✅ 95% minimum coverage
- ✅ All tests must pass
- ✅ Coverage report generated (JSON + HTML)

**Artifacts:**
- `backend-coverage-report/` - HTML coverage visualization

---

### 2. Auth Service Tests (`auth-tests`)
**Trigger:** Running on Ubuntu latest with Python 3.12

```bash
cd auth
uv pip install -e ".[dev]"
python -m pytest tests/test_supabase_proxy_api_database.py --cov=src --cov-fail-under=95
```

**Requirements:**
- ✅ 95% minimum coverage on auth core modules
- ✅ All unit tests must pass
- ✅ Includes security, database, and proxy coverage

**Artifacts:**
- `auth-coverage-report/` - HTML coverage visualization

---

### 3. GIFTs Tests (`gifts-tests`)
**Trigger:** Running on Ubuntu latest with Python 3.11

```bash
cd GIFTs
pip install -e .
python -m pytest tests/ --cov=gifts --cov-fail-under=95
```

**Requirements:**
- ✅ 95% minimum coverage (optional, allows warnings)
- ✅ Tests validate gift validation and formats
- ℹ️ Non-critical for build (continues on error)

**Artifacts:**
- `gifts-coverage-report/` - HTML coverage visualization

---

### 4. Frontend Tests (`frontend-tests`)
**Trigger:** Running on Ubuntu latest with Node.js 18

```bash
cd frontend
npm install --legacy-peer-deps
npm run test:coverage
```

**Requirements:**
- ✅ 95% minimum coverage
- ✅ All unit tests must pass with Vitest
- ✅ Coverage threshold checked from output

**Artifacts:**
- `frontend-coverage-report/` - Coverage visualization

---

### 5. Coverage Enforcement (`coverage-enforcement`)
**Depends On:** All test jobs

Validates that critical projects (backend, auth, frontend) all meet 95% coverage requirement.

**Abort conditions:**
- ❌ Backend coverage < 95%
- ❌ Auth coverage < 95%
- ❌ Frontend coverage < 95%

**Success condition:**
- ✅ All three critical projects meet 95%

---

### 6. Build & Push Docker (`build-and-push`)
**Trigger:** Only on:
- Push to `main` or `dev` branch (not PRs)
- Coverage enforcement passes

Builds and pushes to container registry:
- Backend Docker image
- Auth service Docker image

**Labels Added:**
```dockerfile
LABEL version=latest \
      coverage=95+ \
      test-requirement=passed
```

---

### 7. Test Summary (`test-summary`)
**Final report** with:
- ✅/❌ Status for each project
- Coverage percentage displayed
- Overall pass/fail verdict
- Docker build status

## Coverage Thresholds

| Project | Threshold | Tool | Config File |
|---------|-----------|------|-------------|
| Backend | 95% | pytest-cov | `backend/pyproject.toml` |
| Auth | 95% | pytest-cov | `auth/pyproject.toml` |
| GIFTs | 95% | pytest-cov | `GIFTs/pyproject.toml` |
| Frontend | 95% | Vitest | `frontend/vitest.config.ts` |

## Failure Scenarios

### ❌ Backend fails coverage check
```
Pipeline Blocks:
- Coverage enforcement fails
- Docker build skipped
- PR cannot be merged
```

**Fix:** Add tests to `backend/tests/` until coverage ≥ 95%

### ❌ Auth service fails coverage check
```
Pipeline Blocks:
- Coverage enforcement fails
- Docker build skipped
- PR cannot be merged
```

**Fix:** Add tests to `auth/tests/test_supabase_proxy_api_database.py`

### ❌ Frontend fails coverage check
```
Pipeline Blocks:
- Coverage enforcement fails
- Docker build skipped
- PR cannot be merged
```

**Fix:** Add tests to `frontend/src/` using Vitest

### ⚠️ GIFTs fails coverage check
```
Pipeline Continues:
- Warning generated
- Docker build proceeds
- PR can be merged
```

**Note:** GIFTs is optional (non-critical path)

## Viewing Coverage Reports

After tests complete, artifacts are available:

1. **Backend:** Download `backend-coverage-report` → Open `index.html`
2. **Auth:** Download `auth-coverage-report` → Open `index.html`
3. **GIFTs:** Download `gifts-coverage-report` → Open `index.html`
4. **Frontend:** Download `frontend-coverage-report` → Check coverage summary

## Local Testing Before Push

### Test locally to catch issues early:

**Backend:**
```bash
cd backend
python -m pytest tests/ --cov=src --cov-report=html --cov-fail-under=95
open htmlcov/index.html  # View coverage report
```

**Auth:**
```bash
cd auth
python -m pytest tests/test_supabase_proxy_api_database.py --cov=src --cov-report=html --cov-fail-under=95
open htmlcov/index.html
```

**Frontend:**
```bash
cd frontend
npm run test:coverage
# Check output for coverage percentage
```

## GitHub Actions Secrets

No additional secrets required. Pipeline uses `GITHUB_TOKEN` for:
- Container registry authentication
- Artifact uploads

## Branch Rules

Pipeline runs on:
- ✅ Push to `main`
- ✅ Push to `dev`
- ✅ Pull requests to `main` or `dev`

Docker build only on:
- ✅ Push to `main` or `dev` (not PRs)
- ✅ Coverage enforcement passes

## Updating Coverage Requirements

To change the 95% threshold globally:

Edit `.github/workflows/ci-cd.yml` line 10:
```yaml
COVERAGE_THRESHOLD: 95  # Change to desired percentage
```

Or update per-project in their `pyproject.toml`:
```toml
[tool.pytest.ini_options]
# ... existing config ...
addopts = "--cov-fail-under=95"  # Change threshold here
```

## Troubleshooting

### "Coverage below 95%"
1. Check the coverage report artifact
2. Find uncovered lines in HTML report
3. Add tests for those lines
4. Push to trigger pipeline again

### "Frontend coverage check always fails"
1. Verify `npm run test:coverage` works locally
2. Check test-output.log artifact
3. Ensure vitest.config.ts is properly configured

### "Docker build never runs"
1. Verify branch is `main` or `dev`
2. Verify coverage-enforcement job passed
3. Check that this is a push event (not PR)

## Success Criteria

Pipeline is successful when:

✅ **All Tests Pass:**
- Backend: ≥95% coverage
- Auth: ≥95% coverage
- Frontend: ≥95% coverage

✅ **Coverage Enforcement Passes:**
- All critical projects meet threshold

✅ **Docker Build Succeeds:**
- Backend image pushed
- Auth image pushed

✅ **Summary Generated:**
- Final report shows all green

## See Also

- [Backend README](../../backend/README.md)
- [Auth README](../../auth/README.md)
- [Frontend README](../../frontend/README.md)
- [GIFTs README](../../GIFTs/README.md)
