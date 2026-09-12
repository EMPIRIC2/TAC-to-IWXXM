# Context: Epic #922 synthesis — architecture investigation complete

> **Status**: Accepted (EV-922-synthesis / 2026-09-03)  
> **Tickets**: [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922) (epic)  
> **Corpus**: [Corpus: system-spec] §Platform logical layers · [Corpus: adr] ADR-037–042

## Summary

Epic #922 **investigation band is complete**. Six child spikes (#923, #924, #925, #926, #927, #931) produced ADR-037–042. Option C (logical layers, no package renames) holds across all spikes. Runtime implementation and Platform UIs (#933–#938) are **out of epic scope** — tracked as follow-on evolve/build cycles.

## Epic acceptance (contract band)

| Criterion | Met |
|-----------|-----|
| Spikes closed with ADR | Yes — ADR-037–042 (PRs #1125–#1130) |
| Gap matrix vs ADR-030 | Yes — see session `reports/922-epic-synthesis.md` |
| Milestone sequence approved | Yes — Core → Profiles → Validation → Adapters → Dissemination → Workflows → UIs |
| No ADR-030 / #912 contradiction | Yes — ADR-036 semantic/exchange preserved |

**Close epic when:** PRs #1125–#1130 merge to `stage`; close child issues #923–#931.

## PR merge order

```text
#1125 (ADR-037) → #1126 → #1127 → #1128 → #1129 → #1130 (ADR-042)
```

Rebase stacked PRs after each merge. If intermediate ADRs already on `stage`, rebase #1130 to single ADR-042 commit.

## Runtime follow-ons (priority)

1. `packages/workflows` executor (ADR-042)
2. DisseminationGateway façade + plan runtime (ADR-041)
3. MappingConfig source/sink runtime (ADR-040)
4. PipelineResult unified runtime (ADR-039)
5. ConversionProfile loader (ADR-038)

## Platform UI unblocking

| Issue | Unblocks after |
|-------|----------------|
| #933 ConversionProfile editor | ADR-038 on `stage` (+ #914 for full scope) |
| #934 Workflow builder | ADR-042 on `stage` + workflows runtime MVP |
| #936 Dissemination ops | ADR-041/040 on `stage` |
| #938 Pipeline inspector | ADR-039 on `stage` |

## References

- Session report: `~/.cursor/workflow/.../EV-922-epic-synthesis/reports/922-epic-synthesis.md`
- Original layout spike: [platform-package-layout-923](platform-package-layout-923.md)
- ADRs: [ADR-037](../adr/ADR-037-platform-logical-layers.md) through [ADR-042](../adr/ADR-042-workflow-definitions.md)
