# Catalog row template

Paste into `docs/domain/rules/RULE_SOURCE_URLS.md` (and/or issue comments). Fill every field.

```markdown
### {title}
- **Publisher:**
- **URL:**                    # permanent / versioned landing preferred
- **Stable concept pattern:** # e.g. http://codes.wmo.int/iwxxm/{Register}/{notation}
- **Access:**                 # public | captcha | register | paywall
- **Applies to:** products=[METAR,SPECI,TAF,SIGMET,AIRMET,VAA,TCA]; profiles=[annex3|iwxxm_us]; role=[validation|conversion|iwxxm-validation|bulletin]
- **Gap vs GIFTs:**
- **Consumer:** tac-validate | tac2iwxxm | iwxxm-validate | UI-decode | bulletin
- **Label:** normative | normative-vocabulary | normative-schema | normative-conversion-notes | normative-examples | normative-exchange | informative | historical-GIFTs
- **Caveats:**
- **Mined:** YYYY-MM-DD · pin/tag if schemas · ticket #N
```

## Compact issue-comment paste block

```text
### {title}
- Publisher:
- URL:
- Stable concept pattern:
- Access: public | paywall | …
- Applies to: products=[…]; profiles=[…]; role=[…]
- Gap vs GIFTs:
- Consumer: tac-validate | tac2iwxxm | iwxxm-validate | UI-decode
- Label: …
- Caveats:
```
