# Exchange header and translation metadata audit

Session: EV-1275-exchange-audit. Ticket: #1275. Scale: micro. Gate: open.

[Corpus: product §F6] [Corpus: product §F16] [Corpus: domain-profiles] [Corpus: adr/ADR-036]

Judged against `stage` after #1276, #1277, #1274, and the follow-ups #1290, #1291, and #1292. Sources: the 5th-edition OPMET IWXXM exchange guidelines (mining notes) and the WMO abbreviated-heading filename `A_TTAAiiCCCCYYGGggBBB_C_CCCC_YYYYMMddhhmmss.xml.gz`. This note does not change the converter.

## Checklist

| Item | Mark | What is already true |
|------|------|----------------------|
| `permissibleUsage` for operational, test, and exercise reports | present | A successful convert stays operational unless the TAC has an explicit test or exercise marker. Those reports are non-operational, with reason `TEST` or `EXERCISE` and a short supplementary note. A failed translation stays operational. |
| `translationCentreName` and `translationCentreDesignator` only when translating for another State | partial | Ordinary success omits them. On-behalf success writes the caller's centre. A failed shell with a parsed heading writes that heading and the caller's centre, including empty strings when none was supplied. A failed shell with no heading omits the centre unless the caller supplied one. It does not write `YUZZ`. |
| Translation time | partial | On-behalf success writes `translationTime` from the same clock as the heading when a heading was parsed. A failed shell always writes a time. Ordinary in-state success omits it. |
| Partial translation and `translationFailedTAC` | present | A failed shell keeps the original TAC and does not include the weather parameters. METAR and SPECI have issue time, aerodrome, and observation time. TAF has a valid period. SIGMET and AIRMET have an issuing unit and a valid period. VAA, TCA, and SWXA have their issuing centre. |
| Abbreviated heading and the FTBP filename | present | Bulletin convert with a parsed heading suggests `A_…xml.gz` using the IWXXM T1T2. A paste with no heading invents nothing. The Canada MSC name stays `.xml`. |
| Gzip | present | When the suggested filename ends in `.xml.gz`, gzip bytes of the IWXXM document sit beside the XML text. A Canada `.xml` name stays plain XML. |
| T1T2 designators LA, LP, LC, LT, LS, LV, LY, LW, LK, LU, LN | present | The bulletin map sends SA→LA, SP→LP, FC→LC, FT→LT, WS→LS, WV→LV, WC→LY, WA→LW, FK→LK, FV→LU, FN→LN. VONA uses LM, which is outside this list. |
| AMHS: one file-transfer body part, IPM heading extensions, no AFTN | out of scope | Transport stays on milestone 2. Not a follow-up from this audit. |
| Authorized aerodrome or FIR name, and optionally position, when translating for another State | partial | The report carries the ICAO indicator. Coordinate lookup stays on #1271. This audit does not add a name field. |

## Follow-up

No converter edit under #1275. The in-scope gaps filed from this audit are on `stage`:

- [#1290](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1290) — a failed translation with no heading omits the fictional centre.
- [#1291](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1291) — a `.xml.gz` suggested filename has gzip bytes beside the XML text.
- [#1292](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1292) — failed shells carry the guidelines' minimum identity fields.

Translation time on a failed shell, and an aerodrome or FIR name beyond the ICAO indicator, stay partial. They are not new tickets from this note.

## Out of scope

AMHS send, dissemination changes, filename-generation changes in this ticket, turning the app into an operational translation centre, statistics and retention, and promoting `stage` to `main`.
