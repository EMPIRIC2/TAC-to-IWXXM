<!-- TEMPLATE: test-plan.md -->
<!-- Instructions: Replace all [bracketed placeholders] with project-specific content. -->
<!-- Remove this comment block before finalizing. -->

# Test Plan

> **Project**: [Project Name]
> **Repository**: [Repository URL]
> **Last updated**: [Date]

## Scope

**In scope**: [What this test plan covers — e.g., core pipeline validation, paper result reproduction]

**Out of scope**: [What this test plan does not cover — e.g., UI testing, performance benchmarking]

## User Journeys (E2E)

Product-facing journeys are defined in [user-journeys.md](user-journeys.md) (UJ-001–…).
Map each journey to test modules under `tests/e2e/` and TC-IDs below.

| Journey | Feature | Local E2E module | live E2E | Test plan TC |
|---------|---------|------------------|-----------|--------------|
| UJ-001 | F# | `test_uj001_*.py` | [optional] | TC-001 |

## Connectivity & wiring (multi-app / UI)

If static frontends call APIs on **different origins**, document tiers per
`.cursor/skills/connectivity-gates.md`:

| Tier | Scope | Command |
|------|-------|---------|
| H0c | CORS policy (in-process) | `pytest tests/unit/test_cors_policy.py` |
| H0i | Cross-service integration | `pytest tests/integration` |
| H4 | Live CORS preflight | `pytest tests/smoke/test_staging_connectivity.py -m live` |
| H5 | Frontend bundle URLs | `scripts/deploy/verify_connectivity.sh` |

Vitest/component tests are **not** a substitute for H4–H5.

## Test Strategy

| Level | Framework | Scope | Run Command | Est. Duration |
|-------|-----------|-------|-------------|---------------|
| Smoke | [framework] | Basic pipeline executes without error | `[command]` | [time] |
| Unit | [framework] | Individual functions and modules | `[command]` | [time] |
| Integration | [framework] | End-to-end pipeline stages | `[command]` | [time] |
| Validation | [framework] | Reproduce paper results | `[command]` | [time] |

## Test Cases

### TC-001: [Smoke Test Name]

- **Objective**: Verify the pipeline runs end-to-end without crashing
- **Preconditions**: [What must be set up first]
- **Input**: [Input files, parameters, or commands]
- **Steps**:
  1. [Step 1]
  2. [Step 2]
- **Expected output**: [What success looks like]
- **Pass criteria**: [Specific measurable condition]
- **Source**: [Paper §X] or [Repo: test file]

### TC-002: [Unit Test Name]

- **Objective**: [What this test validates]
- **Preconditions**: [What must be set up first]
- **Input**: [Input files, parameters, or commands]
- **Steps**:
  1. [Step 1]
  2. [Step 2]
- **Expected output**: [What success looks like]
- **Pass criteria**: [Specific measurable condition]
- **Source**: [Paper §X] or [Repo: test file]

### TC-003: [Validation Test — Paper Reproduction]

- **Objective**: Reproduce [specific result] from the paper
- **Preconditions**: [Dataset, corpus fixtures, hardware requirements]
- **Input**: [Exact inputs used in the paper]
- **Steps**:
  1. [Step 1]
  2. [Step 2]
- **Expected output**: [Paper-reported values with tolerance]
- **Pass criteria**: [Metric] within [tolerance] of paper-reported [value]
- **Source**: [Paper §X, Table Y, Figure Z]

## Test Data

| Dataset | Source | Size | Format | How to Obtain |
|---------|--------|------|--------|---------------|
| [name] | [URL or path] | [size] | [format] | [download/generate instructions] |

### Test Fixtures

- Location: `[path to test fixtures in repo]`
- Generation: `[command to generate fixtures if needed]`

## Metrics & Thresholds

| Metric | Threshold | Context | Paper Reference |
|--------|-----------|---------|-----------------|
| [metric] | [value] | [when this applies] | [Paper §X] |

## Environment Requirements

| Resource | Minimum | Recommended | Notes |
|----------|---------|-------------|-------|
| GPU | [spec] | [spec] | Required for [which tests] |
| RAM | [spec] | [spec] | |
| Disk | [spec] | [spec] | For test data storage |

## CI Integration

- **CI system**: [GitHub Actions / GitLab CI / etc.]
- **Test jobs**: [List of CI jobs that run tests]
- **Reproduce CI locally**: `[command]`

## Known Gaps

- [ ] ⚠️ [Gap 1 — what's missing and why]
- [ ] ⚠️ [Gap 2 — what's missing and why]
