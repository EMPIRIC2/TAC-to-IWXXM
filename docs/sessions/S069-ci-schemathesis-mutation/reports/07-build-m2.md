# 07-build M2 — Mutation (#874)

> Session: S069-ci-schemathesis-mutation | Cycle: EV-059 | 2026-08-17  
> Corpus: [Corpus: product §F34] [Corpus: tests] [Corpus: tech-spec]

## Status

M1 Schemathesis merged via PR [#997](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/997) → `stage`
(`c08bc30f`). M2 mutation scaffolding + PoC complete; PR for #874 follows.

## Delivered (T2.1–T2.3)

| Task | Result |
|------|--------|
| T2.1 | `pytest-gremlins==1.9.0`; Stryker `@stryker-mutator/{core,vitest-runner,typescript-checker}@10.0.0`; `make test-mutation*` |
| T2.2 | `.github/workflows/mutation.yml` — schedule `0 5 * * *` + `workflow_dispatch`; chunked Python + JS matrix; ≤25 min/job; soft 1200s script timeout |
| T2.3 | PoC runs + survivor handling (below); 08 + PR → `stage` |

## Local / CI knobs

- `make test-mutation-poc` — narrow Python (`env.py`)
- `make test-mutation-python TARGET=…`
- `make test-mutation-js TARGET=frontend|shared`
- Env: `MUTATION_TIMEOUT_SEC`, `GREMLIN_EXTRA_ARGS`

## PoC results

### Python (`poc-shared-env`)

- Target: `packages/shared/src/metar_shared/env.py`
- Result: **4/4 zapped (100%)**, 0 survivors
- Note: nested package `pyproject.toml` shifts pytest rootdir — script forces
  `--rootdir` + absolute `--gremlin-targets`

### TypeScript (`packages/shared` / `src/index.ts`)

- Result: **23 killed / 3 survived** (score 88.46%)
- Survivors are **equivalent mutants** on `parseCommaSeparatedOrigins` outer
  `trim` / empty short-circuit (behavior identical after `split`+`map(trim)`+`filter`):

| Mutant | Change | Why waived |
|--------|--------|------------|
| MethodExpression | `raw.trim()` → `raw` | Whitespace-only inputs still empty after per-part trim+filter |
| ConditionalExpression | `if (!trimmed)` → `if (false)` | Empty string path still yields `[]` via filter |
| BlockStatement | empty `if (!trimmed) {}` | Same as above |

**Waiver** (`D-S069-m2-survivors`): accept equivalent survivors; do not weaken
coverage≥95%; full nightly matrix may surface more survivors — fix via
bug-investigation or waive in follow-ups (not every-PR gate).

## Exclusions

e2e, Rust crates, generated `iwxxm_xsd` trees — documented in
`[tool.pytest-gremlins]` and Stryker `mutate`/`ignorePatterns`.

## Next

Open PR #874 → `stage`; after merge close #874 and epic #841; Lean `08-verify-build`
on this PR; promote held.
