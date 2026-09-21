# Engineering — what to work on now

Ticket-tuned index for agents and humans. Prefer open GitHub issues over historical session reports.

**Live agent state:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/{id}/`  
**Standing corpus:** [CORPUS.md](../CORPUS.md)  
**Project board:** [project-board.md](../project-board.md) · [Project #7](https://github.com/orgs/EMPIRIC2/projects/7) (20 h/week · I01=2026-09-15)  
**Active sessions:** EV-yaml-full-configurability ([#1226](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1226) full YAML + emit ADR-047); EV-profile-builder-workbench-edit ([#1203](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1203) / F7.w IDE workbench); EV-080-param-conversion-templates (#1146); EV-project-board-planning; prior slim PR [#1185](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1185)

## Open epics / high priority (snapshot 2026-09-21)

| Issue | Theme |
|-------|--------|
| [#1226](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1226) | **Active** — Full YAML configurability + convert emit (ADR-047 Proposed; M1–M5 #1227–#1231) |
| [#1203](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1203) | **Active** — Profile Builder IDE workbench + full five-library editability (F7.w) |
| [#1196](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1196) | YAML/DnD Profile Builder lineage (Phase A on stage via #1197; DnD superseded by #1203) |
| [#1198](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1198) | National Conversion XSD mining (blocked on vendor pins) |
| [#1031](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1031) | CA_ECCC — mine MSC IWXXM PDFs |
| [#1030](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1030) | CA_ECCC — mine MANAIR |
| [#1029](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1029) | CA_ECCC — mine MANOBS |
| [#1028](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1028) | CA_ECCC — mine datamart |
| [#1120](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1120) | Epic — profile-scoped lint/validation catalog |
| [#1146](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1146) | Epic — composable conversion blocks (**active:** EV-080 phase-1 templates + bridge) |
| [#1147](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1147) | Epic — workflow blocks in ConversionProfile |
| [#962](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/962) | Epic — US gov adoption readiness |
| [#1058](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1058) | Spike — many exchanges / marketplace architecture |
| [#1097](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1097) | Epic (backlog) — in-app marketplace |
| [#1159](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1159) | UI — SIGMET examples OUTPUT_VALIDATION_WARNING |
| [#1149](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1149) | UI — profile counts / catalog error states |

Refresh this table when starting a cycle (`gh issue list`). Do not treat closed tickets or archived session trees as scope authority.

## Engineering spine (always)

| Need | Doc |
|------|-----|
| Features / scope | [feature-list.md](../feature-list.md) |
| Architecture | [spec.md](../spec.md) |
| Env / deploy / deps | [tech-spec.md](../tech-spec.md) + satellites |
| HTTP | OpenAPI + [api-contract.md](../api-contract.md) quirks |
| Gates | [test-plan.md](../test-plan.md) |
| Docstrings | [docstrings.md](docstrings.md) |

## Domain (opt-in)

Load [domain/](../domain/) only for mining / profile tickets (e.g. #1028–1031, #1120).
