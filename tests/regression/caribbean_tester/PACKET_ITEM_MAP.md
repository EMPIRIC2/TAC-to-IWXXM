# Caribbean tester packet → regression map

Machine-readable twin: `fixtures/PACKET_ITEM_MAP.json`.

Every questionnaire row, N-series item, Downloads file, and screenshot maps to at least one test node (or an explicit DEFERRED status).

## Completeness

See JSON `pct_with_tests` (**97.9%** with tests; 5 deferred walkthrough/auth/empty-popup items). Non-deferred items without tests: **0**.

## Interop policies (single product truth)

| Topic | Policy | Test |
|-------|--------|------|
| Soft preview vs publish | Soft preview never equals Valid; `OUTPUT_VALIDATION_WARNING` blocks download | `test_interop_policies.py`, FE `resultCard` / `IwxxmPreviewPane` |
| RMK annex3 vs iwxxm_us | annex3 emits `REMARKS_EXCLUDED`; iwxxm_us may retain | `test_annex3_excludes_rmk_while_iwxxm_us_may_retain` |
| GTS / AHL | Library peels AHL for METAR/SPECI/TAF; TT must match product (SA≠SPECI) | cross-product GTS tests + heading_paste |
| SIGMET CNL vs DECR | CNL → `isCancelReport`; DECR → `WEAKEN` | `test_sigmet_cnl_and_decr_coexist_as_distinct_behaviors` |
| VRB units | Keep `[kn_i]` | cross-product VRB tests |

## UX categories

| Category | Status |
|----------|--------|
| Soft-preview honesty | Addressed (FE + interop) |
| Publish / download gate | Addressed (`OUTPUT_VALIDATION_WARNING`) |
| Validate-on-TAC message | Addressed (wellformed TAC detect) |
| New TAC mode reset / top bar | Addressed in FileConverter diff |
| Operator instructions | One-pager updated |
| Busy UI / results stacking | Partial — mockup-aligned status card exists; full redesign deferred |
| Empty validation pop-up | Deferred — no stable repro |
| Walkthrough product | Deferred |
| Internal EV-/ADR ids in UI | Guarded (EV-048); screenshots of older builds showed ids — current FE guards |

## Image review

All **65** PNG/JPEG under Downloads were opened with the vision Read tool (15 Jamaica + 50 Guyana). Summary: `fixtures/IMAGE_REVIEW.md`.

[Corpus: product §F6] [Corpus: product §F7] [Corpus: product §F10] [Corpus: tests]
