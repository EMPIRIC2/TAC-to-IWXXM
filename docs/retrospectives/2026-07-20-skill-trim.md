# Retrospective — 2026-07-20 skill trim (RET-001)

> Session: [S017-skill-trim-retro](../sessions/S017-skill-trim-retro/) · Cycle **RET-001**  
> Depth: **Light** · Scope: custom (00, 16, 14, pipeline, protocol, legacy twins)  
> AskQuestion: **waived** (`D-S017-RET001-aq-waive`) — user written blanket approval

## Evidence digest

- ~60 recent agent sessions: heavy `16-evolve` / `00-context` / state-manager churn; fat skill `@`-attach common.
- Lean routing already worked on S016 (`00→16→01→02→10→13`).
- Legacy twins still selectable (`build-executor`, etc.) alongside numbered stages.
- No prior `docs/retrospectives/` reports.

## Themes confirmed (user)

1. Archive/stub legacy twins  
2. Lean / Standard / Full presets (Lean default)  
3. Split fat skills (`14-hotfix`, `00-context`, `pipeline`)  
4. Shared protocol card  
5. CORPUS-first stage opens; domain opt-in  
6. Batch workflow-state updates  
7. Stop full skill body attach  

## Actions (RA)

| ID | Action | Target | Priority | Status |
|----|--------|--------|----------|--------|
| RA-001 | Stub legacy twins + archive full text | `.cursor/skills/{legacy}/`, `_archive/` | P1 | **done** |
| RA-002 | Add protocol-card.md | `.cursor/skills/protocol-card.md` | P1 | **done** |
| RA-003 | Lean/Standard/Full presets | `00-context`, `16-evolve`, `docs/skill-routing.md` | P1 | **done** |
| RA-004 | Split 14-hotfix / 00-context / pipeline | `SKILL.md` + `reference.md` | P1 | **done** |
| RA-005 | CORPUS-first + batch state in preamble/protocol | `pipeline-preamble.md`, `workflow-state-agent-protocol.md` | P1 | **done** |
| RA-006 | Document “don’t @-attach full skills” | protocol-card, 16-evolve output rules | P2 | **done** |
| RA-007 | Resume S016/EV-012 after S017 close | workflow-state | P1 | open (after close) |

## Skill updates

| Path | Status | Summary |
|------|--------|---------|
| `protocol-card.md` | applied | New short shared card |
| `_archive/*` + 7 stubs | applied | Redirects; `disable-model-invocation: true` |
| `00-context/SKILL.md` | applied | ~88 lines; detail → `reference.md` |
| `14-hotfix/SKILL.md` | applied | ~71 lines; detail → `reference.md` |
| `pipeline/SKILL.md` | applied | ~73 lines; detail → `reference.md` |
| `16-evolve/SKILL.md` | applied | Presets, Lean checkpoints, corpus-touched-only |
| `pipeline-preamble.md` | applied | Card-first, CORPUS band, legacy note, batch state |
| `workflow-state-agent-protocol.md` | applied | Start+exit batching |
| `docs/skill-routing.md` | applied | Presets + legacy table |

## Interview responses

Blanket approval of proposed change list in chat (prior turn + `/17-retrospective Approve all…`). Light depth — no per-stage interview.

## Follow-up

- Close S017; resume paused **S016** / EV-012 (`13-deploy-smoke`, PR #746).
- Optional later: slim other stage skills (01–13) to protocol-card pattern (backlog only).
