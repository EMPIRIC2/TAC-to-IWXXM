# Access friction & citation rules

**Ticket:** [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719)  
**Policy:** URLs and paraphrased citations only — **never** commit full Annex 3 / Manual on Codes / Doc 8896 PDF text.

---

## Access by source class

| Source | Access | Friction | How we cite in-repo |
|--------|--------|----------|---------------------|
| **ICAO Annex 3** | ICAO Store purchase | **Paywall**; account required | Title, edition, store URL, section numbers when known — no redistributed PDF |
| **ICAO Doc 8896 / 10003 / 9766** | ICAO Store | **Paywall** | Same |
| **WMO-No. 306** (Vol I.1 / I.3) | WMO e-Library | Public catalog; viewer often **slider captcha** | Official `library.wmo.int/idurl/…` + mining notes; local extracts **gitignored** under `.local/reference/` |
| **WMO-No. 49 Vol II** | Discontinued | SARPs moved to **Annex 3** (2023) | Cite discontinuation page; keep `codes.wmo.int/49-2` as **vocabulary** namespace only |
| **codes.wmo.int** | Public Linked Data | None | Stable `http://codes.wmo.int/…` URIs; offline RDF already in vendor |
| **schemas.wmo.int / wmo-im/iwxxm** | Public HTTP + GitHub | None | Pin tag from `vendor/manifest.json` (`v2025-2`) |
| **iwxxm-translation** | Public GitHub | None | Label **informative** (no official WMO/ICAO status) |
| **FMH-1** | Public OFCM/ICAMS PDF | None | Handbook URL; still do not claim ICAO copyright |
| **iwxxm-us** | Public nws.weather.gov | None | Pin 3.0 tarball SHA in manifest |
| **NWS Codes Registry** | Public | None | `codes.nws.noaa.gov/FMH-1` |

---

## Citation patterns (safe)

```markdown
Per ICAO Annex 3 (store: https://store.icao.int/en/annex-3-…) §{section}: …
NilReason: `http://codes.wmo.int/common/nil/missing`
Schema: https://schemas.wmo.int/iwxxm/2025-2/metarSpeci.xsd
```

### Do

- Prefer **landing pages** that survive edition bumps (store / library / schemas root)
- Record **edition / tag / date mined** when citing paywalled or versioned docs
- Point operators to purchase official ICAO docs when they need full prose
- Use vendored mirrors for offline CI (`vendor/schemas/*`)

### Do not

- Paste multi-page excerpts from Annex 3 / Doc 8896 / Manual on Codes into git
- Scrape ICAO Store PDFs into `docs/` or fixtures
- Treat unofficial mirror PDFs (third-party sites) as normative SoT
- Treat GIFTs sources as ongoing SoT (ADR-014)

---

## Local reference layout (optional, gitignored)

| Path | Contents |
|------|----------|
| `.local/reference/wmo-306-vI-3-2023/` | PDF + `fulltext.txt` + extracts |
| `.local/reference/icao-doc-10003-draft-en/` | Advance 2014 unedited Doc 10003 PDF + extract |
| Tracked notes | `docs/domain/iwxxm/WMO-306-vI-3-2023-mining-notes.md` · `docs/domain/iwxxm/ICAO-Doc-10003-draft-2014-mining-notes.md` |

Ensure `.gitignore` covers `.local/reference/` before storing PDFs.

---

## Paywall rows for design consumers (#698 / #699 / #693)

When a rule needs Annex 3 prose and only a store URL exists:

1. Catalog row labeled **normative** + **Access: paywall**
2. Implementer cites section when licensed copy available
3. For CI/fixtures, prefer **public** equivalents: official TAC examples, codes.wmo.int, Schematron — not bootleg Annex text
4. Operator-facing errors (#702) may say “per ICAO Annex 3” without quoting long passages

---

## License notes (non-legal summary)

| Content | Practical handling |
|---------|-------------------|
| ICAO Annexes / Docs | Copyright ICAO — purchase/license; cite, don’t mirror |
| WMO Manual on Codes | WMO copyright — library access; cite paragraphs, don’t commit scans |
| codes.wmo.int / schemas.wmo.int | Public for linked data / schema consume; don’t rehost entire registries |
| FMH-1 / iwxxm-us | US government / NWS materials — public URLs OK; still no need to copy full schemas beyond vendor pin sync |
