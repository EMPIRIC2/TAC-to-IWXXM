# Evolve summary — S070 / EV-060

> Closed: 2026-08-18 · `D-S070-13` · `D-S070-close`  
> Product: [#1007](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1007) → `stage` @ `6ef540bc`  
> Staging CD: [32183276810](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32183276810)  
> Standing report: [docs/evolve-report-EV-060.md](../../../evolve-report-EV-060.md)

## Shipped

| Ticket | Outcome |
|--------|---------|
| #1001 | AHL heading lint as COM; split contained TAC reports; `INVALID_AHL` for malformed |
| #1003 | Additive `product=iwxxm` pass-through (convert no-op / lint XML; F7.t) |
| #1002 | Labeled Profile control at converter top |
| #1005 | Editable Bulletin ID / Issuing Center (CCCC validation) |
| #1004 | Wire convert `log_level` to package/stdlib loggers (redact Authorization) |
| #1006 | Auth UAT + restore `POST /auth/logout` for FileConverter sign-out |
| #1000 | Epic closed on S070 closeout |

## Verify

| Stage | Verdict |
|-------|---------|
| Spec→Build | open (`D-S070-spec-build=1a`) |
| 07–11 | PASS (M1–M4; 11 user approve converter + Auth) |
| 12-verify-deploy | PASS checklist (`D-S070-12-*`; merge deferred then approved at 13) |
| 13-deploy-smoke | PASS (`D-S070-13`) — H0c–H5 + live UJ-059..063 / TC-EV060-1006 14/14 |

## Deferred

- Promote `stage`→`main` (explicit AskQuestion later)
- Chore: fix `tests/live/test_tc_live_f6_030_bulletin.py` multipart field `file` → `files`

## Corpus

[Corpus: product §F7] [Corpus: product §F6] [Corpus: product §F2] [Corpus: product §F31] [Corpus: journeys] [Corpus: tests] [Corpus: deploy] [Corpus: adr/ADR-034] [Corpus: decisions §EV-060]
