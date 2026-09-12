# AHL / bulletin API design note — tac2iwxxm surface (T0.5)

**Date**: 2026-08-01  
**Task**: T0.5 · **TC**: TC-EV029-003 · **Lock**: E29-T2=1 (AHL lives in `tac2iwxxm`)  
**Cycle**: EV-029 / S036 · **Issue**: [#823](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/823)  
**Canonical rules**: [IWXXM_CONVERSION §AHL / bulletin](../../../../domain/IWXXM_CONVERSION.md#ahl--bulletin-canonical-ev-029)

Design only — **no M1 code in this task**. Implementation: **M1** (T1.1–T1.4).

---

## 1. Goals

1. One **shared** AHL parse / format / map / filename helper in `packages/tac2iwxxm`.  
2. `packages/dissemination` **imports** that API (no FastAPI/Supabase; keep package boundary).  
3. Cover all eight-family + SWXA `T1T2` pairs; BBB prefix families; IWXXM AMHS filename.  
4. Reject GIFTs-style over-broad BBB (`[ACR]{2}[A-Z]` as sole gate) — use AHL page v1.0.1 prefixes.

---

## 2. Current surface (as-of T0.5)

| Location | What exists | Gap |
|----------|-------------|-----|
| `tac2iwxxm.bulletin.split_bulletin` | Parse AHL + split `=` reports | **METAR/SPECI only**; BBB regex `[ACR]{2}[A-Z]` |
| `tac2iwxxm.models.BulletinMeta` | `ahl, tt, aa, cccc, yygggg, bbb, report_count` | No `ii`; no IWXXM `T1T2`; no `reportStatus` |
| `dissemination.edis.format_wmo_ahl` | Format AHL line (any `tt`) | Duplicate of future tac2iwxxm formatter; BBB still broad |
| Dissemination COLLECT | `bulletinIdentifier` on COLLECT XML | Filename builder not shared |

Public exports today (`tac2iwxxm.__init__`): `split_bulletin`, `BulletinMeta`, `BulletinSplit`, `BulletinSplitError`.

---

## 3. Proposed public API (M1)

Keep names stable where possible; add helpers as new exports.

```text
tac2iwxxm.bulletin
├── parse_ahl(line|text) -> AhlParts          # NEW (or extend BulletinMeta)
├── format_ahl(parts) -> str                  # NEW — supersede dissemination.edis.format_wmo_ahl
├── map_t1t2(tac_tt) -> iwxxm_tt              # NEW — table from AHL page
├── bbb_to_report_status(bbb) -> ReportStatus # NEW — AA*/CC*/RR*/absent
├── iwxxm_filename(...) -> str                # NEW — A_…xml[.gz]
├── split_bulletin(text, *, product) -> BulletinSplit  # EXTEND product set
└── BulletinSplitError                        # unchanged codes
```

### 3.1 `AhlParts` / `BulletinMeta` fields

| Field | Meaning |
|-------|---------|
| `tt` | TAC or IWXXM `T1T2` as parsed (document which) |
| `aa` | `A1A2` |
| `ii` | `ii` (2 digits) — **add** (today only in regex, not on meta) |
| `cccc` | Originating centre |
| `yygggg` | `YYGGgg` |
| `bbb` | Optional; validated against prefix families |
| `ahl` | Full heading line |
| `iwxxm_tt` | Mapped L* designator (derived) |
| `report_status` | NORMAL / AMENDMENT / CORRECTION (derived; not CNL/NIL) |

Additive msgspec fields preferred (API contract `bulletin_meta` may need a thin delta in M1).

### 3.2 Product → AHL dialect + report splitter

| Product | TAC `tt` | Body recognizer (M1+) |
|---------|----------|------------------------|
| METAR | SA | existing METAR…`=` |
| SPECI | SP | existing SPECI…`=` |
| TAF | FC/FT | `TAF`…`=` (multi later) |
| SIGMET gen | WS | FIR SIGMET form…`=` |
| VA SIGMET | WV | VA SIGMET…`=` |
| TC SIGMET | WC | TC SIGMET…`=` |
| AIRMET | WA | AIRMET…`=` |
| VAA | FV | `VA ADVISORY` block (may span lines; `=` optional) |
| TCA | FK | `TC ADVISORY` block |
| SWXA | FN | `SWX ADVISORY` block |

`split_bulletin(..., product=)` remains the operator entry; unsupported product →
`BulletinSplitError(code="bulletin_split_failed")` until that family's splitter lands
(M1 ships shared parse/map/filename; per-family body split can land with M2–M11 if needed,
but **AHL parse + T1T2 map + BBB + filename must land in M1**).

### 3.3 BBB validation (replace over-broad gate)

Accept:

- absent  
- `RRx` / `AAx` / `CCx` with x ∈ A…X  
- document Y/Z special (accept or reject per AHL page — fixture in T1.1)

Reject: tokens that are not those families (including bare `A`/`C` and GIFTs-wide patterns
that accept invalid third letters outside A–X where the page forbids them).

Map: `AAx`→AMENDMENT, `CCx`→CORRECTION, absent/`RRx`→NORMAL.

### 3.4 Filename helper

```text
A_{iwxxm_tt}{aa}{ii}{cccc}{yygggg}[{bbb}]_C_{cccc}_{yyyyMMddhhmmss}[_{ffffff}].xml[.gz]
```

Inputs: `AhlParts` (with `iwxxm_tt`) + UTC timestamp + optional fractional + `gzip: bool`.  
Dissemination / COLLECT `bulletinIdentifier` SHOULD use this helper (M1 or follow-up in
dissemination thin adapter — **no** reimplementation of T1T2 map).

---

## 4. Dissemination migration (E29-T2)

| Step | Action |
|------|--------|
| M1 | Add `format_ahl` / `parse_ahl` / maps in `tac2iwxxm` |
| M1 | `dissemination.edis.format_wmo_ahl` → thin wrapper calling `tac2iwxxm` **or** deprecate + re-export |
| Constraint | `dissemination` must not import FastAPI; may depend on `tac2iwxxm` (check pyproject — add if missing via AskQuestion / inventory) |
| Tests | Keep EDIS ASCII tests green; add T1T2 map unit tests in tac2iwxxm |

If adding a dependency edge `dissemination → tac2iwxxm` is new, confirm against
`docs/dependency-inventory.md` in M1 (AskQuestion if not listed).

---

## 5. ADR stance

Prefer **amend existing** ADR covering F6.bulletin / dissemination writer-contract
rather than a new ADR, unless the shared API shape is controversial in M1 review
(E29-T2 interview lock). Record amend in M1 docs task if needed.

---

## 6. Fixture plan (feeds T1.1)

| Case | Expect |
|------|--------|
| Accept: each TAC `T1T2` in §3.2 (minimal AHL line) | parse + `map_t1t2` |
| Accept: `CCA` / `AAA` / `RRA` | COR / AMD / NORMAL |
| Reject: invalid BBB | `bulletin_split_failed` or dedicated lint code |
| Filename: SA→LA segment | `A_LA…` not `A_SA…` |
| Negative: unsupported product body | clear error |
| METAR multi (regression) | TC-F6-030 still green |

---

## 7. Out of scope (T0.5 / M1)

- SIGWX / VONA / QVACI convert  
- FE Examples unlock for SWXA (M11 / TC-EV029-008)  
- Changing COLLECT GML packing rules beyond identifier/filename helper  
- Paywall Annex 3 full text

---

## 8. Exit → T0.6

This note is the M0 design SoT for AHL. **T0.6** M0 exit checklist confirms no HARD gap
blocks Phase B; M1 may then start T1.1 fixtures.
