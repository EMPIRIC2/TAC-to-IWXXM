# ADR-037: Platform logical layers — keep package layout (epic #922 / spike #923)

> **Status**: Accepted (EV-922 / #923)  
> **Date**: 2026-09-03  
> **Deciders**: User (EV-922 AskQuestion — Option C)  
> **Related**: [ADR-013](ADR-013-tac2iwxxm-package-architecture.md), [ADR-030](ADR-030-dissemination-package-architecture.md), [ADR-036](ADR-036-semantic-vs-exchange-profiles.md)  
> **Issues**: [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922), [#923](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/923)  
> **Write-up**: session `reports/923-platform-package-layout.md` (EV-922)

## Context

Epic [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922) proposes a platform layering model:

**Core → Profiles → Validation → Adapters → Dissemination**

Spike [#923](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/923) asked whether the monorepo should be restructured into new packages (`core`, `conversion`, `validation`, `adapters`, `gateways`/`afs`, `dissemination`, `profiles`) or keep the current tree.

Constraints:

- Published PyPI names and import paths (`tac2iwxxm`, `tac-validate`, `iwxxm-validate`, `dissemination`)
- Template / plan-adherence approved locations
- Sibling contract spikes still open (#924 ConversionProfile, #925 canonical MET, #926 SQL adapters, #927 DisseminationGateway)
- Must not break F21 public paths or package purity (no FastAPI/Supabase in MET libs)

## Decision

1. **Option C — logical layers only (M5 / this spike).** Keep current `packages/*` names and uv workspace members. Document a **logical layer map** in `[Corpus: system-spec]` that aliases epic #922 layers onto existing packages and `docs/domain/profiles/`.

2. **Reject Option A (big-bang restructure)** for the foreseeable M5 window — cost outweighs benefit before contracts exist.

3. **Defer Option B (incremental rename/split)** until #924–#927 close with ADRs. Any future B move requires a new evolve + ADR amend; this ADR does **not** authorize package moves.

4. **Milestone sequence (draft — revise after siblings):**

   ```text
   Core → Profiles (#912/#924) → Validation (#925) → Adapters (#926) → Dissemination (#927) → Workflows (#931) → Platform UIs (#933–#938)
   ```

5. **No migrate-now child issues** from #923 unless a later cycle explicitly Approves Option B/A.

## Alternatives considered

| # | Alternative | Why rejected / deferred |
|---|-------------|-------------------------|
| A | Big-bang new package tree | Breaks PyPI, imports, CI, template rules; premature vs open spikes |
| B | Incremental split now | Contracts (#924–#927) not closed; defer |
| C | Logical layers documentation | **Accepted** — matches tree; unblocks epic hygiene |

## Consequences

### Positive

- Clear narrative for AMS / M5 without disruptive renames
- Epic #922 acceptance item “milestone sequence” can be marked via #923 write-up + this ADR
- Sibling spikes stay focused on contracts, not file moves

### Negative / follow-ups

- Layer names in epic prose won’t match directory names — always cite the system-spec map
- Future Option B must update template-conformance + plan-adherence + PyPI publish paths carefully

## References

- [Context: platform-package-layout-923](../context/platform-package-layout-923.md)
- EV-922 session report `923-platform-package-layout.md`
- [Corpus: product] F6, F16–F19
