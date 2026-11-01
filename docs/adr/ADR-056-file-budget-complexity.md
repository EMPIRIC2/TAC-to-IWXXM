# ADR-056: File line budget ≤500 + complexity caps

## Status: Accepted

**Session:** EV-file-budget-complexity  
**Answers:** L0 tooling only; P0 splits deferred (parent recommended options 1–8)

## Context

Hand-written modules under `apps/` and `packages/` have grown far beyond a maintainable size (dozens of files over 500 lines; several over 2000). There was no CI or lint rule enforcing a file line budget or cyclomatic complexity cap. Generated xsdata under `packages/shared/.../iwxxm_xsd/` (ADR-027) and OpenAPI `.d.ts` must stay out of any budget. Workspace lint ownership lives in root `pyproject.toml` (ADR-053).

This is workspace tooling under [Corpus: product §M5] and [Corpus: tech-spec], not a new product feature.

**Numbering note:** ADR-054 is severity-strict-ui; ADR-055 is inherit-factory. This decision is **ADR-056**.

## Decision

1. **Hard line budget:** ≤ **500** physical lines per hand-written source file under `apps/` and `packages/`.
2. **CI policy:** Fail when any non-allowlisted path exceeds 500 lines. Bootstrap grandfather allowlist: `config/file-budget-allowlist.txt`. Checker: `scripts/ci/check_file_budget.py` (`make file-budget`).
3. **Exclusions (fixed):** `**/iwxxm_xsd/**`, `apps/frontend/src/generated/**`, `apps/frontend/src/app/components/ui/**` (shadcn), build/coverage/vendor trees.
4. **Complexity:** Ruff `C901` with `max-complexity = 10` enforced via dedicated `config/ruff-complexity.toml` + `scripts/ci/check_file_complexity.py` (avoids nested package `per-file-ignores` replacing root). ESLint `complexity` 10 and `max-lines` 500 for frontend app source (allowlisted / `ui/` overridden). Existing over-complexity is grandfathered until splits land.
5. **SoC / splits:** Remediating allowlisted files is AskQuestion-gated (batch by package). L0 does not split FileConverter or other P0 modules.
6. **Tests:** Same ≤500 budget for new/changed tests; existing oversize tests stay on the allowlist.

## Consequences

- New mega-files cannot land unnoticed.
- Remediating the inventory is multi-cycle work; tooling ships first.
- Sibling evolves update the allowlist in the same PR when they intentionally move or split paths.
- Agents follow `.cursor/rules/optional/file-budget.mdc`.

## Alternatives considered

- Soft-warn only in CI. Rejected: warnings are ignored.
- Fail all oversize files immediately. Rejected: blocks unrelated delivery.
- Budget generated xsdata. Rejected: ADR-027 codegen.
- Putting `C901` only in root `select`. Rejected for L0: nested package `per-file-ignores` replace parent keys and drop grandfather entries.

## References

- Inventory: session `EV-file-budget-complexity` → `reports/oversized-file-inventory.md`
- [Corpus: product §M5] [Corpus: tech-spec] [Corpus: adr/ADR-053] [Corpus: adr/ADR-027] [Corpus: adr/ADR-048]
