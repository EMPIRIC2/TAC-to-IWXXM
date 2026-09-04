# EV-098 — CA_ECCC deep mining (#1028–#1031)

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-09-02 | Domain deepen under **F36** / `CA_ECCC` | Highest open P1 mining children after #916 P1 close |
| 2026-09-02 | Cover **#1028, #1029, #1030, #1031** in one evolve | Shared promote path; datamart+PDFs inform MANOBS/MANAIR |
| 2026-09-02 | Research via **deep-research-domain-handoff** (EV-097) | Gates A→B→C; emit handoff prompts; paste findings for B |
| 2026-09-02 | Promote only via **mine-domain-sources** after gate C | Fail-closed; no silent SoT edits |
| 2026-09-02 | Workstream order **#1028 → #1031 → #1029 → #1030** | Schema/PDF evidence before TAC rule promotion |
| 2026-09-02 | Build intent: notes + provenance + stubs + **P0 fixtures** | Matches #1029 AC; stubs alone insufficient |
| 2026-09-02 | Skip **build/e2e** / waive H4–H5 | No UI this cycle; protect existing CA_ECCC paths |
| 2026-09-02 | No full copyrighted annex/PDF prose in git | Cite + section pointers only ([ACCESS_AND_CITATION](../domain/rules/ACCESS_AND_CITATION.md)) |
| 2026-09-02 | SIGMET national layer & VAA stay OOS | Per #1030; prior EV-074/077 validate-first holds |
| 2026-09-02 | Must not break IWXXM **3.0.0** + `iwxxm-ca` pin | ADR-036 CA_ECCC architecture |

## REQs (approved)

| ID | Issue | Requirement |
|----|-------|-------------|
| R1 | #1028 | Datamart tree fully triaged + promotion backlog |
| R2 | #1031 | All MSC `doc/` PDFs triaged; `eccc-iwxxm-doc-pdfs-mining-notes.md` |
| R3 | #1029 | MANOBS section notes; P0 (`VIS.SM`, `ALT.A`, `AUTO`) → catalog + fixture pairs |
| R4 | #1030 | MANAIR TAF/AIRMET notes; ≥1 TAF national extension + AIRMET GFA ↔ code-ca |
| R5 | all | Durable URLs in `RULE_SOURCE_URLS` / `PROVENANCE_MAP`; no full copyrighted prose |
| R6 | all | Promote only after handoff gates A→B→C via mine-domain-sources |

## Related

- Scoped brief: [docs/context/ev-098-ca-eccc-mining.md](../context/ev-098-ca-eccc-mining.md)
- Session: `EV-098-ca-eccc-mining`
- Skill: `.cursor/skills/deep-research-domain-handoff/`
- Prior: EV-064 / #916; EV-097 handoff skill

[Corpus: decisions] [Corpus: product §F36] [Corpus: domain-profiles]
