# Build Plan Card

> Cycle: EV-061 | Session: S071-pre-promote-ux-catalog | Updated: 2026-08-18  
> Active: Spec / 04-tech-plan — first Build batch **M1 #1011** after Spec→Build opens

## Goal

Ship epic #1009 children to `stage`. First Build batch: live bulletin harness multipart
field `files` (#1011). Promote held until #1015.

## Constraints

- [Corpus: api] [Corpus: tests §TC-LIVE-F6-030] [Corpus: product §F6]
- Branch `evolve/EV-061-pre-promote-ux-catalog` → PRs to `stage`; promote held
- No new deps / ADR / CORS origins
- Spec→Build **closed** until dual Spec + gate AskQuestion

## In scope (this batch — M1)

- [ ] T1.1 — Test — Assert live harness posts multipart `files` — Spec: [Corpus: tests §TC-LIVE-F6-030]
- [ ] T1.2 — Code — Change `file` → `files` in `tests/live/test_tc_live_f6_030_bulletin.py` — Spec: #1011

## Out of scope (explicit)

#996 click-detail; #837 mini-map; M1+ national profiles; dissemination spikes; auto-promote;
product AHL decode (#1012) is **M2**

## Parallelism

T1.1 → T1.2 (TDD). Single-file chore; no parallel agents.

## Verify / PR

08-verify-build M1 after T1.1–T1.2; small PR to `stage` or stack with M2 if still Spec-blocked.

## Gate

Spec→Build **closed**. Do not implement T1.2 product code until the gate opens.
