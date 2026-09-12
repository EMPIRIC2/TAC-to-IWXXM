# Coverage Uplift Plan to 95%

This plan defines module-by-module work needed to reach and sustain 95% coverage
for backend, auth, frontend, and GIFTs under immediate hard-fail CI gates.

## Policy

- Coverage gates are immediate and strict at 95% for all services.
- No reduction in thresholds is allowed.
- Each PR should increase or preserve coverage in touched modules.

## Service Workstreams

### 1. Backend (highest gap)

Target order:
1. `src/api.py`
2. `src/services/validation_orchestrator.py`
3. `src/services/validation.py`
4. `src/utilities/conversion.py`
5. `src/utilities/gifts_adapter.py`
6. remaining `src/services/*` and `src/utilities/*`

Test strategy:
- Isolated unit tests with dependency mocking for external IO.
- FastAPI endpoint tests with focused fixtures for auth/db mocks.
- Conversion regression matrix (valid/invalid/COR edge cases).

### 2. Auth

Target order:
1. `src/api.py`
2. `src/supabase_proxy.py`
3. `src/observability.py`

Test strategy:
- Endpoint tests with mocked Supabase responses.
- Token/session and password lifecycle edge cases.
- Error-path observability assertions.

### 3. Frontend

Target order:
1. API utilities and auth state flows.
2. Core conversion/upload components.
3. Form validation and error states.

Test strategy:
- Vitest component tests with React Testing Library.
- API mocking for backend/auth interactions.
- Keep Playwright for integration confidence.

### 4. GIFTs

Target order:
1. Decoder/encoder branch completion gaps.
2. Validation helpers and utility modules.

Test strategy:
- Fixture-driven parser tests.
- Edge-case coverage for malformed TAC and uncommon report variants.

## Required Commands

Run these locally before push:

```bash
make test-unit-backend
make test-unit-auth
make test-unit-frontend
make test-unit-gifts
make test-integration
```

## Tracking

For each service, track:
- current coverage percent
- modules completed in this sprint
- modules remaining
- blocker dependencies

Update this file with weekly checkpoints until all services are >=95%.
