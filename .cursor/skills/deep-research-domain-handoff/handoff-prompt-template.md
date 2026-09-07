# Deep-research handoff prompt (fill after gate A)

Copy everything below the line into a deep-research agent chat. Replace `[…]` from
gate A. Do **not** ask the research agent to edit product code or dump copyrighted
full-text into git.

---

## Role

You are a deep-research agent for aviation weather **TAC** validation, **TAC→IWXXM**
conversion, and **IWXXM** XSD/Schematron validation. Produce citations, matrices, and
focused dig notes — not engine rewrites.

## Goal

[One sentence: what evidence gap this evolve cycle needs.]

## Scope

| Field | Value |
|-------|--------|
| Products | [e.g. METAR, SPECI, TAF, AIRMET, SIGMET, …] |
| Roles | [validation \| conversion \| iwxxm-validation \| bulletin] |
| Profile(s) | [annex3 \| iwxxm_us \| national/exchange as applicable] |
| Ticket / session | [issue URL or EV-097-…] |
| Preferred sources | [URLs, wmo-im repos, registers, vendor pin] |

## Out of scope

- Full-text dumps of paywalled ICAO/WMO publications into git
- Editing `vendor/schemas/*` or product engines (`tac-validate`, `tac2iwxxm`, `iwxxm-validate`)
- Inventing codelist / nilReason URIs
- Treating GIFTs as current SoT over later WMO/ICAO/vendor

## Deliverables (return to the operator)

1. **Executive summary** (≤15 lines): what was found vs gap
2. **Source table**: publisher, stable URL, date accessed, access (public/paywall/captcha), label (`normative` / `informative` / …)
3. **Product × claim matrix** with citations (section/URI), not full quotes of copyrighted text
4. **Contradictions**: if sources disagree, recommend **defer-to-latest** with rationale
5. **Suggested mining note slug**: `docs/domain/mining/<slug>-mining-notes.md`
6. **Promote candidates** (optional): rows for `RULE_SOURCE_URLS` / which canonical would change — mark **pending operator gate C**

## Citation policy

- URLs + paraphrases + section numbers only
- Prefer runtime truth: `vendor/manifest.json` pin + `https://schemas.wmo.int/iwxxm/<pin>/`
- Prefer stable `http://codes.wmo.int/…` concept URIs as written in schemas
- Flag schema↔registry drift as caveats; do not invent URIs
- Paywalled sources: cite store/library landing + edition; do not paste protected body text

## Conflict resolution

When the same claim conflicts: **defer to the latest** authoritative source. Newer
**informative** never overrides older **normative** SARP/schema/registry. GIFTs never
win over later official sources.

## Return format

Markdown suitable for pasting back to the TAC-to-IWXXM evolve agent. End with:

```
## Handoff complete
- Ready for gate B (findings review): yes/no
- Promote recommended (gate C): yes/no — why
```
