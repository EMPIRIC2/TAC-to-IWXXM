# Feasibility — EV-yaml-engine-configurability (#1224)

**Verdict:** **Feasible** as scoped (honesty + usability; no emit-YAML rewrite).

[Corpus: product §F2/F6/F9/F12/F15] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046] [Corpus: tech-spec]

## Evidence

| Concern | Finding |
|---------|---------|
| Overlay loaders | Already exist (`TAC_*_DIR` / `IWXXM_VALIDATE_POLICY_DIR` / `TAC2IWXXM_PROFILE_DIR`) — Build is docs/examples/preflight on top |
| Fail-closed merge | ADR-045/046 + extension-header cycle already specify behavior |
| HTTP risk | No new wire fields; TC-EVYEC-004 is a regression lock |
| Matrix honesty | Convert emit + many detectors remain Python — documenting that is the point |
| Effort | Standard Spec + thin Build (docs, templates, script, tests) — no FE/H4–H5 |
| Risks | Over-claiming “full YAML” in README copy; dual glossary drift — mitigated by TC-EVYEC-002/005 |

## Non-goals stay out

ADR-044 editor · HTTP policy YAML · Schematron-as-YAML · #1222 · convert-emit YAML · detector deepen

## Recommendation

Proceed to **tech-plan** (preflight entrypoint layout, example overlay tree, matrix CI lock paths). Gate remains closed until documenting verify.
