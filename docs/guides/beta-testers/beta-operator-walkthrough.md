---
marp: true
paginate: true
---

# TAC → IWXXM Translator Prototype: tester walkthrough (slide outline)

Detailed deck for a live session with participating Services, about 20–30 minutes
including questions. Speaker notes are reproduced under each slide.
Caribbean Meteorological Organization Headquarters, in partnership with Brown University.
Author: Joe McGuire · joseph_mcguire@brown.edu · Brown University.

Products in scope: METAR, SPECI, TAF, SIGMET. All output is test output and is not
operationally authoritative.

- Built deck: `beta-operator-walkthrough.pptx`
- Content sources: the CMO two-week Testing and Evaluation Guide, plus
  [`../operator-handbook.md`](../operator-handbook.md) and [`../operator-one-pager.md`](../operator-one-pager.md)
- UI figures: [`SCREENSHOTS.md`](./SCREENSHOTS.md), rendered panels, swappable for real captures

This outline lists slide text and speaker notes; the UI panels on each slide are named
in `SCREENSHOTS.md`.

---

<!-- Slide 1 -->
## TAC → IWXXM

- PROTOTYPE

- Translator prototype: two-week testing and evaluation

- Caribbean Meteorological Organization Headquarters, in partnership with Brown University

- https://app.tac-to-iwxxm.com

- A

- How to operate

- Get in and succeed once

- B

- What you can do

- The rest of the prototype

- UI panels in this deck are rendered from the production interface. Labels, options and sample text are the live ones.

- C

- Testing and reporting

- The two weeks, and what to send back

- Allow 20–30 minutes, including questions.

- Joe McGuire · joseph_mcguire@brown.edu · Brown University

### Speaker notes

Welcome, and thank you for taking part.

This is a prototype TAC-to-IWXXM translator developed by CMO Headquarters with Brown University, to help Member States get ready for exchanging aeronautical meteorological information in IWXXM.

Over the next two weeks we are asking you to use it the way you would use a real tool, and tell us where it falls short. The conversion, validation and downloads are real. What they are not is operationally authoritative. Nothing produced here goes out as an official product.

Three parts: how to operate it, what else it does, and what we need recorded and sent back. Interrupt at any point.

---

<!-- Slide 2 -->
`WELCOME`
## Why we are doing this

- CMO Headquarters and Brown University have built a prototype translator to support Member States in preparing for IWXXM exchange.
- These two weeks assess its functionality, accuracy, validation and usability.
- The result is a consolidated picture of what needs improving before anything wider is considered.
- Your Service’s findings feed directly into that, particularly the failures.

- REAL

- Real conversion and validation
- Real downloads you keep
- Runs on the production site

- UNDER TEST

- Labels and defaults may change
- Product coverage varies
- That is what you are here to find

- Treat everything the prototype produces as test output. It is not operationally authoritative.

### Speaker notes

Set the frame before anyone touches the app.

This is a joint CMO / Brown prototype, and the point of the exercise is readiness: can Services in this region take their existing TAC and produce IWXXM that is correct and valid.

What is real: the production site, the real conversion engine, real schema and rule validation. Files you download are genuine IWXXM.

Everything else is under test: wording, defaults, how much of each product family is covered, how clearly errors are reported.

Say the bottom line out loud. Test output is not authoritative. Nothing here changes what your Service disseminates.

---

<!-- Slide 3 -->
`WELCOME`
## Products in scope, and how to test them

- PRODUCTS IN SCOPE

- TESTING PRINCIPLES

- Use both the representative messages from CMO Headquarters and actual TAC from normal operations.
- Record successes and failures. Failures and unexpected results are the most valuable findings.
- Where you can, compare the generated IWXXM against the source TAC to check the meteorological information survived.
- Run alongside existing processes; change nothing about operational TAC production or dissemination.

- METAR

- SPECI

- Routine aerodrome report

- Special aerodrome report

- TAF

- SIGMET

- Aerodrome forecast

- En-route hazard information

- Test all four during the period. No message volume is prescribed. Exercise the translator against the normal range your Service produces.

### Speaker notes

Four products, and only four, for this evaluation: METAR, SPECI, TAF and SIGMET. The picker in the app offers more; anything else is out of scope here.

Two sources of test material. CMO Headquarters supplies a representative set, and that is Week 1. Then your own operational TAC, the real traffic your Service produces, and that is Week 2.

The principle people most often get wrong is the second one: record what worked too. A log full of only failures tells us nothing about coverage.

And the fourth is a hard rule. This runs in parallel. Nothing about how you produce or disseminate TAC changes during these two weeks.

---

<!-- Slide 4 -->
`WELCOME`
## How the two weeks run

- WEEK 1

- WEEK 2

- END OF WEEK 3

- Familiarisation and basic functionality

- Operational parallel testing

- Submission

- Work through the representative METAR, SPECI, TAF and SIGMET set from CMO Headquarters.
- Generate IWXXM and run the applicable validation checks.
- Record every result in the Test Log.

- Use actual TAC your Service produces in normal operations.
- Run in parallel; change nothing about operational production or dissemination.
- Record translation, validation and accuracy results.

- Your Service focal point submits the completed Test Log.
- Plus any Error Reports and the User Evaluation Questionnaire.
- CMO consolidates the results with Brown University.

- Identify your Service focal point now. That is who collates the Test Log and submits it.

### Speaker notes

Week 1 is deliberately controlled: the same representative set everywhere, so results are comparable across Services. Get familiar, confirm the basics work, log everything.

Week 2 is where the real value is. Your own operational messages will contain things the representative set does not: local conventions, unusual groups, products at the edge of the format. That is exactly what we need to see.

Note the submission date on the third card. The testing runs two weeks; the completed Test Log, any Error Reports and the User Evaluation Questionnaire are due from the focal point at the end of Week 3, which leaves a week to collate.

If you have not already, agree now who your focal point is.

---

<!-- Slide 5 -->
## How to operate

- PART A

- Get in, and get one product right, start to finish.

### Speaker notes

This part is deliberately narrow: one operator, one report, from paste to a validated file on disk. Everything else can wait until they have done it once.

---

<!-- Slide 6 -->
`PART A: HOW TO OPERATE`
## Getting in

- https://app.tac-to-iwxxm.com

- tac-to-iwxxm.com redirects to the same place. No install; a current browser is enough.

- GUEST

- SIGNED IN

- Nothing to set up
- No cloud history
- Drafts live in this browser only

- Saved work sessions
- History you can reopen
- Folder / ZIP mass upload

- Shared workstation? Open Privacy settings in the footer first. Guest work can be kept in this browser until you clear it.

- Use the account your Service issued. Never share a password by chat or email.

### Speaker notes

Open the production URL. The banner across the top is the app being honest about guest mode: progress may be lost, and local drafts stay on this device until you log in.

For a two-week evaluation, sign in. You will want to reopen your own tests, and guest work is not recoverable once the browser is cleared.

The privacy point matters on a shared operational position. Guest work history can be stored in this browser and preferences are stored locally. Privacy settings in the footer controls that. Check it before you start, not after.

On accounts: use the credentials your Service issued. If sign-in fails, check the URL and caps lock, then go to your local IT or MET systems contact. Nobody sends passwords around.

---

<!-- Slide 7 -->
`PART A: HOW TO OPERATE`
## Tour of the shell

- Convert

- The workbench: console, options, preview, results.

- History

- My METARs: your drafts and finished work.

- Quality metrics

- Compare output against official WMO examples.

- Validation Issues Catalog

- Look up what a validation or lint message means.

- Dissemination ops

- Sending. Not used during this evaluation.

- Conversion profiles

- What each profile encodes, at a glance.

- Header, right-hand side: HELP · PREFERENCES · Theme · SIGN IN

### Speaker notes

Six tabs along the top. For this evaluation, only the first three matter much.

Convert is where you will spend your time. History is your own work, and it is where you will go back to find a test you want to write up. Quality metrics compares the app against official WMO example products, and we will come back to it.

The Validation Issues Catalog is a lookup for messages you do not recognise. Dissemination ops we are not using. Conversion profiles shows what each profile does.

Top right: HELP opens the operator one-pager, PREFERENCES holds your options including privacy, Theme is light and dark, SIGN IN on the far right.

---

<!-- Slide 8 -->
`PART A: HOW TO OPERATE`
## Three ways to get TAC into the app

- Type or paste

- 1

- Straight into the console. One report per entry, terminated with “=”.

- Upload a file

- 2

- Drop zone under the console: .txt, .metar, .tac, .xml, .gz, .zip. Select files, a folder, or a ZIP.

- Load a demo example

- 3

- The Examples picker loads a known-good sample. Best way to learn the app without risking your own text.

- Mass upload of a whole folder or ZIP requires signing in, which is useful for the Week 1 representative set.

### Speaker notes

Demonstrate the demo example first: it removes the fear of doing it wrong.

Typing or pasting is the everyday path for a single report. The one thing that catches people is the terminator: each report ends with an equals sign. If Convert gives you nothing, check that first.

The drop zone takes files. For Week 1, if you are signed in you can point it at the whole representative set as a folder or ZIP rather than one at a time.

The Examples picker loads a sample known to convert cleanly. If something fails afterwards, you know the difference is your text, not the app.

---

<!-- Slide 9 -->
`PART A: HOW TO OPERATE`
## Product type, profile, exchange profile

- PRODUCT TYPE

- Which product you are converting, or Auto-detect, which reads it from the report.

- The encoding rules: the international Annex 3 line, or your State’s profile.

- PROFILE

- EXCHANGE PROFILE

- How the output is packaged for exchange in your region.

- Use what your Service expects, and keep it the same across your tests, and record the settings with each result.

### Speaker notes

Three selectors, and testers over-think them. Keep it simple.

Product type: leave it on Auto-detect unless you are deliberately forcing a type. If auto-detect picks the wrong one for a real report, that is a finding. Keep the report.

Profile: the encoding rule set. There is an international Annex 3 line and a set of State profiles. Use what your Service expects, and use the same one throughout, or your results will not be comparable.

Exchange profile: regional packaging.

These change encoding and packaging only, not destinations and not credentials. And record the settings alongside each test result; a result without its settings is hard to reproduce.

If the default that loads is not what your Service uses, that is worth reporting on its own.

---

<!-- Slide 10 -->
`PART A: HOW TO OPERATE`
## Decode and soft preview

- DECODE

- Plain-language reading of your TAC, plus a code-by-code table. This is the quickest way to check the accuracy question: did the app read your report the way you meant it?

- SOFT PREVIEW

- Best-effort IWXXM while your TAC is still partial, with the spans it could not decode highlighted. Advisory only: it can lag or simplify edge cases. Never record a preview as a test result.

### Speaker notes

This is the slide that prevents the worst mistake in the evaluation, so do not rush it.

The Decode panel reads your TAC back in plain language and explains each group. For the accuracy assessment this is your first check: if the decode says something different from what you meant, the IWXXM will too.

Soft preview is a sketch. It exists so you can see something while a report is half-typed, and it marks the spans it could not decode. The app labels it "not for publish".

Say the rule out loud: the preview is never a test result. If the preview and Convert disagree, Convert and Validate win.

---

<!-- Slide 11 -->
`PART A: HOW TO OPERATE`
## Convert, then read the log

- CONVERT builds the IWXXM XML from what is in the console or in your uploaded files.
- The conversion / validation log opens underneath: Issues first, then Results.
- Issues are graded. Information is worth reading; errors need fixing before you rely on the file.
- Leftover TAC the encoder could not place is reported as residuals. Those are accuracy findings, so record them.
- The counters on the action buttons tell you how many converted files you are holding.

- CONVERT&SEND converts and sends in one action. Do not use it during this evaluation. Convert, then download.

### Speaker notes

Press CONVERT and let the log open. Resist going straight to Download.

The log has two halves. Issues is what the app noticed: some informational, some a real problem. Results is the converted output with its download link.

Residuals deserve attention in this evaluation. If the encoder could not place part of your TAC it says so rather than silently dropping it. A residual on a routine report is an accuracy finding: keep the TAC and the output, and log it.

Build the habit of reading the log every time, even when it converted cleanly. A green result with three information messages still tells you something.

And skip CONVERT&SEND entirely for these two weeks. We are not disseminating anything.

---

<!-- Slide 12 -->
`PART A: HOW TO OPERATE`
## Validate: this is the result you record

- AFTER CONVERT

- Validation results appear with the conversion log. This is the validation outcome for your Test Log.

- ON ITS OWN

- The Validate IWXXM input mode checks IWXXM you already have, useful for a file from elsewhere.

- Validation red means the file is not ready. Read the messages, fix the TAC, or confirm the IWXXM version matches your schema expectation.
- The Validation Issues Catalog tab explains a message if the wording is unfamiliar.
- A validation failure on a well-formed operational report is a Major finding at least. Keep everything.

### Speaker notes

Validation answers one of the five assessment questions directly, so it is never optional here.

Two routes. Normally you validate what you just converted, from the same log, and that is the validation result that goes in the Test Log. Separately, the Validate IWXXM input mode lets you check IWXXM that came from somewhere else.

When validation is red, the messages tell you which problem you have. Two usual causes: the TAC has a real problem, or the IWXXM version does not match what the receiving system expects.

Important for grading: if a perfectly ordinary operational report fails validation, that is not a curiosity, it is a Major finding. And if an element came out wrong or missing, it is Critical. Keep the TAC, the IWXXM and the validation output.

---

<!-- Slide 13 -->
`PART A: HOW TO OPERATE`
## Download and keep the evidence

- Download the .xml from the Results section of the log.
- Converted a batch? DOWNLOAD ZIP takes the whole set in one file.
- Keep the generated IWXXM with the source TAC and the validation result. That trio is what makes a finding reproducible.
- Store them the way your Service stores working material for the evaluation.
- As a guest, download promptly, because clearing the browser can remove local drafts.

- TAC in, IWXXM out, validation result alongside. That is one Test Log entry.

### Speaker notes

Short slide, one message: the evidence matters as much as the outcome.

A single conversion gives you a download link in Results. A batch gives you DOWNLOAD ZIP with a count, so you can tell whether you have all of them.

For anything that failed or looked questionable, keep three things together: the original TAC, the generated IWXXM, and the validation result. A report we cannot reproduce usually goes nowhere.

And if you are working as a guest, download before you close the tab.

---

<!-- Slide 14 -->
## What you can do

- PART B

- History, quality comparison, and the parts you will not use this fortnight.

### Speaker notes

Part A was the single-report path. Part B is what they will discover on their own anyway, so it is better they hear it from us with the caveats attached.

---

<!-- Slide 15 -->
`PART B: WHAT YOU CAN DO`
## Work history: My METARs

- SIGNED IN

- GUEST

- Sessions saved to your account
- Reopen a past test and rework it
- Survives a new browser or machine

- Local history in this browser only
- Clearing site data removes it
- Nothing to recover if it goes

- Filter by status (draft, in progress, finished, failed), or show the trash.
- EXPORT and IMPORT move your local history between browsers.
- Over a two-week evaluation this is how you find a test again when you write it up.

- If history looks empty: you are probably in guest mode, or storage is off in Privacy settings.

### Speaker notes

The History tab is labelled My METARs. Signed in, it is your saved work. As a guest it is a local list in this browser and nothing more.

For this evaluation that difference is practical, not theoretical: you will be writing up tests days after you ran them. Guest mode means clearing site data, switching browsers or moving machines loses them, with no copy on a server to restore.

The status filters are how you find things again. EXPORT and IMPORT exist for moving a local list, occasionally useful on a shared position.

The most common support question is "my history is empty". Almost always guest mode, or storage switched off in Privacy settings.

---

<!-- Slide 16 -->
`PART B: WHAT YOU CAN DO`
## Quality metrics

- Browses official WMO IWXXM example products and shows how this prototype’s output compares.
- Each row carries a match status plus residual, lint and validation counts.
- Open a row for a detail view: Official and Converted side by side, with a readable diff.
- Unchanged sections collapse; expand a hunk, or expand all, when you need context.
- Filter by product to reach the four families in scope.

- Useful for training and for understanding accuracy. It is not a substitute for running Validate on your own conversions.

### Speaker notes

This tab is the one people find most interesting and most easily misread, so lead with what it is for.

It takes the official WMO example products and shows what this prototype produces for the same input, with a match status and counts for residuals, lint and validation. Open a row and you get official and converted XML side by side with a readable diff; identical regions collapse.

It is genuinely useful here, because it shows you what a difference between two IWXXM documents looks like, which is exactly the skill you need for the accuracy assessment on your own reports.

Two honest points. A difference is not automatically a fault; some examples are not scored yet. And a good score here says nothing about the file on your screen. Only Validate does that.

---

<!-- Slide 17 -->
`PART B: WHAT YOU CAN DO`
## The picker offers more than we are testing

- IN SCOPE

- Test the four in scope. If you try another and it behaves oddly, say so, but it does not belong in the Test Log for this evaluation.

- METAR

- SPECI

- TAF

- SIGMET

- ALSO IN THE PICKER

- AIRMET

- VAA

- TCA

- SWXA

- Auto-detect reads the product from the report. If it picks the wrong type for one of the four, keep the report. That is a finding.

- VONA

- IWXXM (validate)

### Speaker notes

The picker lists more product types than this evaluation covers. That is not an invitation.

Four products are in scope: METAR, SPECI, TAF, SIGMET. Those are what CMO will consolidate across Services, and mixing in others makes the results harder to compare.

If curiosity gets the better of you and something misbehaves on another type, mention it informally, but keep the Test Log to the four.

The last entry in the picker is different: IWXXM as an input means handing the app an existing IWXXM file to validate rather than TAC to convert.

And if auto-detect picks the wrong type for one of our four, that is a genuine finding. Keep the report text.

---

<!-- Slide 18 -->
`PART B: WHAT YOU CAN DO`
## Dissemination: not part of this evaluation

- Depending on the deployment, the app may offer destinations after convert: a database upload, or a message pathway.
- During these two weeks you do not use them. Download the XML and keep it.
- Your Service’s operational dissemination continues exactly as it does today, through your existing channels.
- If the panel is hidden or disabled at your site, nothing is wrong.

- SITE-SPECIFIC PANEL
- Not shown here. The drawer and its destinations are configured per site

- Never paste secret connection strings, credentials or destination addresses into a Test Log, an Error Report or a chat message.

### Speaker notes

Keep this short and firm. Sending is out of scope, and half the room may not see the panel at all.

The prototype can offer destinations where a site has configured them. We are not using that. The evaluation produces test output, and test output does not get disseminated, which is also why CONVERT&SEND stays untouched.

Your operational dissemination carries on through whatever you use today. Nothing about it changes.

The warning on the slide applies for the whole fortnight: no credentials, no connection strings, no destination addresses in a Test Log or an Error Report. If something about a destination needs to change, that is your systems contact, not this evaluation.

---

<!-- Slide 19 -->
`PART B: WHAT YOU CAN DO`
## If your site runs automated ingest

- PRIMARY PATH

- MANUAL PASTE

- Automated ingest, where your site runs it. That pipeline stays the route for routine traffic throughout.

- What you use for this evaluation, plus ad-hoc fixes, training and recovery. Not a replacement for the pipeline.

- Testing in parallel means nothing about continuous operations changes for these two weeks.

- Not sure whether ingest is running for your centre? Ask your systems contact. It is not something you can tell from this screen.

### Speaker notes

This matters at some sites only, but it prevents a real operational misunderstanding.

If your centre runs automated near-real-time ingest, that pipeline remains the primary path for routine traffic for the whole fortnight. The converter you are testing is a parallel activity.

The failure mode we want to avoid is someone quietly deciding that pasting reports by hand is now part of the process, while the pipeline everyone else assumes is running has stopped.

Nothing on this screen tells you whether ingest is active. Ask.

---

<!-- Slide 20 -->
## Testing and reporting

- PART C

- What to assess, how to grade it, and what your focal point sends back.

### Speaker notes

Land the plane here. The single most valuable thing a tester does is write down the moment they were confused, while they are still confused, and keep the file that caused it.

---

<!-- Slide 21 -->
`PART C: TESTING AND REPORTING`
## What to assess

- Does the translator convert METAR, SPECI, TAF and SIGMET from TAC to IWXXM?

- FUNCTIONALITY

- Does the IWXXM correctly represent the meteorological information in the original TAC?

- ACCURACY

- Does the IWXXM conform to the applicable schema and validation requirements?

- VALIDATION

- Is the prototype practical and intuitive enough for operational meteorological personnel?

- USABILITY

- Does it identify and report translation problems, unsupported constructs and invalid input?

- ERROR HANDLING

- Every Test Log entry should be classifiable against one of these five. If you cannot place it, write it down anyway and say why.

### Speaker notes

Five dimensions. Read them out. They are the headings CMO will consolidate against, so a tester who has them in mind writes a much more useful log.

Functionality is the crudest: did it convert at all. Accuracy is the one that needs a human: does the IWXXM actually say what the TAC said. Validation is objective and the app gives you the answer. Usability is your professional judgement as an operator, and it is a real finding, not a nicety.

Error handling is the one testers forget to assess. When you feed it something broken on purpose, does it tell you clearly what is wrong? Try that deliberately at least once.

---

<!-- Slide 22 -->
`PART C: TESTING AND REPORTING`
## Recording a result

- Every test goes in the Test Log: the ones that worked as well as the ones that did not.
- For any failed or questionable result, retain the original TAC, the generated IWXXM and the validation result.
- Describe the problem briefly, and say whether it affects translation, validation, accuracy or usability.
- Note the product, the options you used, and the date and time in UTC.
- Week 1 entries come from the representative set; Week 2 entries from your operational traffic. Say which.

- TAC in, IWXXM out, validation result alongside, one line of description. That is a complete entry.

### Speaker notes

The Test Log is the deliverable. A test you ran and did not record did not happen, as far as the consolidation is concerned.

Record the successes too. Without them CMO cannot tell the difference between "this product works" and "nobody tried this product".

For anything that failed or looked wrong, the three artefacts together are what make it reproducible: the TAC you fed in, the IWXXM that came out, and the validation result.

One line of description is enough, as long as it says which of the four areas it touches: translation, validation, accuracy or usability.

And mark whether it was Week 1 representative material or Week 2 operational traffic. That distinction matters when the results are pooled.

---

<!-- Slide 23 -->
`PART C: TESTING AND REPORTING`
## Classifying what you find

- Critical

- An incorrect, missing or materially altered meteorological element, or another issue that could affect the operational meaning of the product.

- For example: A wind group, visibility or cloud layer that comes out wrong, or silently disappears.

- Major

- A significant translation, validation or workflow problem requiring correction before wider operational use.

- For example: A routine report that will not convert, or valid TAC that fails validation.

- A non-critical usability, formatting or other issue that does not affect the meteorological meaning.

- Minor

- For example: A confusing label, an awkward step, cosmetic formatting in the output.

- If you are unsure between two levels, choose the higher one and say why. It is easier for us to downgrade than to notice something we were never told about.

### Speaker notes

Three levels, and the boundary that matters is between Critical and Major.

Critical is about meteorological meaning. If a wind group, a visibility, a cloud layer or a hazard comes out wrong or vanishes, the product now says something different from what the observer or forecaster intended. That is the most serious thing you can find and we want it flagged immediately, not saved for the end.

Major is serious but not meaning-changing: something will not convert, or valid TAC fails validation. It has to be fixed before anyone talks about wider use.

Minor is usability and cosmetics. Still worth logging: a tool operators find awkward at three in the morning is a real problem.

When in doubt, grade up and explain.

---

<!-- Slide 24 -->
`PART C: TESTING AND REPORTING`
## End-of-test submission

- CMO consolidates every Service’s results and works with Brown University to identify technical improvements and priorities for further development.

- TEST LOG

- Every test from both weeks, completed.

- ERROR REPORTS

- For each failed or questionable result, with the TAC, the IWXXM and the validation output retained.

- USER EVALUATION QUESTIONNAIRE

- Anything Critical should reach your focal point as soon as you find it. Do not hold it until the end.

- Your Service’s overall judgement of the prototype.

- Submitted by the designated Service focal point at the end of Week 3.

### Speaker notes

Three things go back, from one person: your designated focal point.

The completed Test Log covering both weeks. Error Reports for anything that failed or looked wrong, with the artefacts attached. And the User Evaluation Questionnaire, which is where your overall judgement as operators goes.

Timing: the testing is two weeks, and submission is at the end of Week 3. That gives the focal point a week to collate. Use it; do not start collating on the last day.

One exception to waiting: if you find something Critical (an element wrong or missing), tell your focal point when you find it. That should not sit in a spreadsheet for a fortnight.

From there CMO pools every Service's results and works with Brown to set priorities.

---

<!-- Slide 25 -->
`PART C: TESTING AND REPORTING`
## Troubleshooting

- SYMPTOM

- WHAT TO TRY

- Convert fails or empty result

- Check the “=” terminator, product type and station groups. Fix lint errors first.

- Validation red

- Read the messages. Fix the TAC, or confirm the IWXXM version matches your schema expectation.

- Preview disagrees with Convert

- Trust Convert and Validate. The preview can lag or simplify edge cases.

- An element is wrong or missing

- Grade it Critical. Keep the TAC, the IWXXM and the validation result, and tell your focal point.

- Cannot sign in

- Confirm the URL, the account and your network. Reset a password only through the approved flow.

- History empty

- Sign in; check Privacy settings; confirm you are not in guest mode.

- Destinations missing

- Expected. They are not used in this evaluation, so download instead.

- Quality metrics empty or error

- Check your network, retry, and note the example name if one row fails.

- Slow or timing out

- Retry once. If it persists, note the time and the product and log it.

### Speaker notes

Do not read this table out. Point at it and pick the two rows the room will actually hit.

The first row accounts for most "it does not work" reports: a missing equals sign at the end of the report.

The fourth row is the one to dwell on, because it is the bridge between troubleshooting and reporting. A wrong or missing element is not a thing to work around. It is the most valuable finding in the whole evaluation.

Everything here is also in the operator handbook, so testers have it in writing.

---

<!-- Slide 26 -->
`PART C: TESTING AND REPORTING`
## Where to get help

- IN THE APP

- HELP in the converter header opens the operator one-pager, the short version of today.

- The operator handbook: sign-in, convert and validate, history, Quality metrics, troubleshooting.

- DAY TO DAY

- Local MET and IT support for accounts and network access.

- YOUR SERVICE

- THIS EVALUATION

- Your Service focal point, and CMO Headquarters.

- Both guides are linked from the app, so what you read is always the current version.

### Speaker notes

Four places, in the order you should try them.

HELP in the header is the fastest. It opens the operator one-pager, essentially a printable version of Part A.

The handbook is the day-to-day manual, including the troubleshooting table.

Accounts, network and workstation questions are local: your MET or IT support owns those.

Anything about the evaluation itself (scope, timing, what counts as Critical, how to fill in the log) goes to your focal point, and from there to CMO Headquarters.

---

<!-- Slide 27 -->
`APPENDIX`
## Glossary

- TAC

- Traditional Alphanumeric Code: the coded text form of a report, such as a METAR.

- IWXXM

- The XML form of the same information, for machine exchange.

- Convert

- Builds the IWXXM XML from your TAC. This produces the file you keep.

- Validate

- Checks the IWXXM against schema and rules. This is the validation result you record.

- Soft preview

- Best-effort IWXXM shown while your TAC is still partial. Advisory only.

- Profile

- The encoding rule set: the international line, or a State profile.

- Residuals

- Leftover TAC the encoder could not place, reported rather than dropped.

- Test Log

- Your record of every test run, successful or not, submitted at the end of Week 3.

- https://app.tac-to-iwxxm.com

- Joe McGuire · joseph_mcguire@brown.edu · Brown University

### Speaker notes

Leave this up while you take questions. It is the vocabulary the rest of the evaluation uses.

The three worth pointing at: Convert versus Validate, soft preview, and the Test Log. If a tester goes away with those straight, the session did its job.
