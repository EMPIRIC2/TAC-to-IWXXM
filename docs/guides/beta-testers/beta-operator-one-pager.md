---
marp: true
paginate: true
---

# TAC → IWXXM Translator Prototype: tester one-pager (slide outline)

Short deck for the two-week testing and evaluation period.
Caribbean Meteorological Organization Headquarters, in partnership with Brown University.
Author: Joe McGuire · joseph_mcguire@brown.edu · Brown University.

Products in scope: METAR, SPECI, TAF, SIGMET. All output is test output and is not
operationally authoritative.

- Built deck: `beta-operator-one-pager.pptx`
- Content sources: the CMO two-week Testing and Evaluation Guide, plus
  [`../operator-one-pager.md`](../operator-one-pager.md)
- UI figures: [`SCREENSHOTS.md`](./SCREENSHOTS.md), rendered panels, swappable for real captures

This outline lists slide text only; the UI panels on each slide are named in `SCREENSHOTS.md`.

---

<!-- Slide 1 -->
## TAC → IWXXM

- PROTOTYPE

- Translator prototype: two-week testing and evaluation

- Caribbean Meteorological Organization Headquarters, in partnership with Brown University

- https://app.tac-to-iwxxm.com

- One sheet · read in under five minutes

- Joe McGuire · joseph_mcguire@brown.edu · Brown University

- UI panels in this deck are rendered from the production interface. Labels, options and sample text are the live ones.

---

<!-- Slide 2 -->
`TESTING AND EVALUATION`
## What is in scope, and what the output is not

- PRODUCTS IN SCOPE

- TESTING PRINCIPLES

- Test both the representative messages from CMO Headquarters and actual TAC your Service produces in normal operations.
- Record successes and failures. Failures and unexpected results are the most valuable findings.
- Where you can, compare the generated IWXXM against the source TAC to check the meteorological information survived.
- Run alongside your existing processes. Do not change or disrupt operational TAC production or dissemination.

- METAR

- SPECI

- Routine aerodrome report

- Special aerodrome report

- TAF

- SIGMET

- Aerodrome forecast

- En-route hazard information

- Everything the prototype produces in these two weeks is test output. It is not operationally authoritative and must not be disseminated as an official product.

---

<!-- Slide 3 -->
`PART A: HOW TO OPERATE`
## Open the app

- https://app.tac-to-iwxxm.com

- tac-to-iwxxm.com redirects here. Any current browser; no install.

- GUEST

- SIGNED IN

- Works right away
- No cloud work history
- Drafts stay in this browser only
- Download before you close the tab

- Saved work sessions
- History you can reopen for rework
- Folder / ZIP mass upload
- Use the account your Service issued

- Signing in is worth it for a two-week evaluation: you will want to reopen your own tests.

- Two-week testing and evaluation

- TAC → IWXXM prototype

---

<!-- Slide 4 -->
`PART A: HOW TO OPERATE`
## Five steps to your first IWXXM file

- Paste or upload

- Type TAC into the console, drop a file, or load a demo example.

- 1

- Set the options

- Product type, profile and IWXXM version your Service expects.

- 2

- 3

- Convert

- The app builds the IWXXM XML and writes a conversion log.

- 4

- Validate

- Run IWXXM validation. This is the validation result you record.

- 5

- Download

- Keep the .xml with the source TAC for your Test Log.

- Terminate each report with “=”. If Convert gives you nothing, that is the first thing to check.

---

<!-- Slide 5 -->
`PART A: HOW TO OPERATE`
## Soft preview vs Convert

- GUIDANCE ONLY

- THE PRODUCT

- Soft preview · live decode · plain language

- Convert, then Validate

- Best-effort IWXXM while your TAC is still partial
- Highlights the spans it could not decode
- Plain-language decode helps you read the TAC
- Never record a preview as a test result

- Builds the IWXXM XML you download and keep
- Writes a conversion / validation log you can read
- Validation catches schema and rule problems
- This is what goes in the Test Log

- If the preview and Convert disagree, trust Convert and Validate.

---

<!-- Slide 6 -->
`PART B: WHAT YOU CAN DO`
## What the prototype gives you

- CONVERT

- VALIDATE

- DOWNLOAD

- The four products in scope, plus the other types the picker offers. Auto-detect reads the type from the report.

- Run IWXXM validation on your conversion, or paste existing IWXXM in to check it.

- One .xml, or a ZIP when you converted a batch. Keep it with the source TAC.

- WORK HISTORY

- QUALITY METRICS

- DESTINATIONS

- My METARs keeps your drafts and finished tests. Cloud history when signed in.

- Compare output against official WMO examples. Useful for accuracy checks, but not a substitute for Validate.

- Not used in this evaluation. Download and keep the file; use your normal operational channels as usual.

- Some panels appear only where a site has enabled them. During the evaluation you never need one: download the XML and keep it.

---

<!-- Slide 7 -->
`PART C: TESTING AND REPORTING`
## How the two weeks run

- WEEK 1

- WEEK 2

- END OF WEEK 3

- Familiarisation and basic functionality

- Operational parallel testing

- Submission

- Work through the representative METAR, SPECI, TAF and SIGMET set from CMO Headquarters.
- Generate IWXXM, run the applicable validation checks.
- Record every result in the Test Log.

- Use actual TAC your Service produces in normal operations.
- Run in parallel; change nothing about operational production or dissemination.
- Record translation, validation and accuracy results.

- Your Service focal point submits the completed Test Log.
- Plus any Error Reports and the User Evaluation Questionnaire.
- CMO consolidates results with Brown University.

- Test all four products during the period. No message volume is prescribed. Exercise the translator against the normal range your Service produces.

---

<!-- Slide 8 -->
`PART C: TESTING AND REPORTING`
## What to assess, and how to grade it

- Functionality

- Accuracy

- Validation

- Usability

- Error handling

- Does it convert METAR, SPECI, TAF and SIGMET at all?

- Does the IWXXM say what the TAC said?

- Does the IWXXM conform to the schema and rules?

- Is it practical for operational staff?

- Does it report problems and unsupported input clearly?

- Critical

- An incorrect, missing or materially altered meteorological element, or anything else that could change the operational meaning of the product.

- Major

- A significant translation, validation or workflow problem that needs correcting before wider operational use.

- Minor

- A usability, formatting or other issue that does not affect the meteorological meaning.

---

<!-- Slide 9 -->
`PART C: TESTING AND REPORTING`
## Recording a result

- Every test goes in the Test Log: the ones that worked as well as the ones that did not.
- For any failed or questionable result, keep the original TAC, the generated IWXXM and the validation result.
- Describe the problem briefly, and say whether it affects translation, validation, accuracy or usability.
- Note the product, the options you used, and the date and time in UTC.

- IN THE APP

- HELP in the converter header opens the operator one-pager.

- DAY TO DAY

- The operator handbook covers sign-in, history, Quality metrics and troubleshooting.

- Never put passwords, connection strings or destination addresses into a Test Log, an Error Report or a chat message.

- YOUR SERVICE

- Your focal point, and local MET / IT support for accounts and network access.

- Questions about the evaluation itself go to your Service focal point or CMO Headquarters.

---

<!-- Slide 10 -->
`PART C: TESTING AND REPORTING`
## If something looks wrong

- SYMPTOM

- WHAT TO TRY

- Convert fails, or the result is empty

- Check the “=” terminator, the product type, and the station groups. Fix lint errors first.

- Validation comes back red

- Read the validation messages. Confirm the IWXXM version matches what your schema expects.

- Preview disagrees with Convert

- Trust Convert and Validate. The preview can lag or simplify edge cases.

- An element is missing or altered

- Record it as Critical, keep the TAC, the IWXXM and the validation result.

- History is empty

- Sign in, then check Privacy settings. Guest work is not kept in the cloud.

- Slow, or it times out

- Retry once. If it persists, note the time and the product and report it.
