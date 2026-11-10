# Documentation standards

> Index: [README.md](README.md) 
> Last updated: 2026-11-10

This document states how writers and agents maintain the engineering docs spine.

## Purpose

Tracked docs under `docs/` must stay short, factual, and usable on a fresh clone.
Folder trees under `docs/` may exist on a developer machine as local feeders.
Those feeders are not the public corpus.

Machine catalogs for profiles, rules, and coverage inventories live under
`config/` and stay tracked.

## Required style

1. Write American English.
2. Prefer ASD-STE100 Issue 9 for editable prose: short sentences, active voice,
 one topic per paragraph. No tool proves full STE compliance. A human must
 still review against Issue 9.
3. Remove avoid-ai-writing P0 and P1 tells from root prose.
4. Do not put planning shorthand, ticket numbers, or internal doc paths in
 operator-visible UI copy or public API error text.
5. Prefer full capability names over private codes. Do not write evolve ids,
 session ids, feature letter-codes, or stage numbers in prose.

## How agents find standing truth

Start at [AGENTS.md](../AGENTS.md) and [README.md](README.md). Cite the named
document that owns the topic. If no document covers the change, stop and decide:
add a doc, waive, or re-scope.

## Root spine vs local feeders vs config

| Kind | Location | Git |
|------|----------|-----|
| Index and contracts | `docs/*.md`, `docs/*.csv` | Tracked |
| Profile catalog | `config/profiles/` | Tracked |
| Rule and provenance catalogs | `config/rules/` | Tracked |
| Coverage inventories | `config/engineering/` | Tracked |
| Domain mining, ops runbooks, engineering notes | `docs/domain/`, `docs/ops/`, `docs/engineering/` | Not tracked |
| Architecture decisions (`docs/adr/`), guides, UX logs, STE dictionary | local trees | Not tracked |
| Full legacy dumps | `docs/local-feeders/` | Not tracked |

## CSV matrices

- [user-journeys.csv](user-journeys.csv) owns journey rows.
- [test-plan.csv](test-plan.csv) owns test-case and coverage rows.
- [risks.csv](risks.csv), [assumptions.csv](assumptions.csv),
 [issues.csv](issues.csv), and [decisions.csv](decisions.csv) own RAID rows.

Markdown companions describe columns and linkage rules only. Do not duplicate
full matrices in Markdown.

## Linkage rule

Every active journey row must point at one or more test ids or a concrete test
path. Every new behavioral capability in
[product-requirements.md](product-requirements.md) must add or update journey
and test rows in the same change set when tests exist.

## Protected regions

Do not rewrite fenced code, inline code, paths, URLs, TAC/IWXXM samples, or
machine-read YAML/JSON/CSV cells for style alone.
