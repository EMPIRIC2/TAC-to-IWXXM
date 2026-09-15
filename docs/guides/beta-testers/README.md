# Tester decks: two-week testing and evaluation

Two presentations for the CMO / Brown University two-week testing and evaluation of the
TAC → IWXXM translator prototype, for operational meteorological personnel at
participating Services.

Author: Joe McGuire · joseph_mcguire@brown.edu · Brown University.
Caribbean Meteorological Organization Headquarters, in partnership with Brown University.

**Products in scope:** METAR, SPECI, TAF, SIGMET. Everything the prototype produces
during the evaluation is test output and is not operationally authoritative.

| Deck | Length | Use |
|---|---|---|
| `beta-operator-one-pager.pptx` | 10 slides | Hand out or skim in under five minutes; prints cleanly |
| `beta-operator-walkthrough.pptx` | 27 slides, with speaker notes | Live walkthrough, about 20–30 minutes including questions |

Both follow the same arc: **Part A, how to operate**; **Part B, what you can do**;
**Part C, testing and reporting** (what to assess, error classification, and the
end-of-Week-3 submission).

The `.md` files here are outline mirrors of the built decks, for review and diffing.
The `.pptx` files are the deliverables.

## Content sources

Content is drawn from, and must stay consistent with:

- The CMO **two-week Testing and Evaluation Guide**: scope, testing principles, the
  week-by-week approach, the five assessment dimensions, error classification and the
  submission path. This is authoritative for anything about the evaluation itself.
- [`../operator-one-pager.md`](../operator-one-pager.md): how to operate the app, short form
- [`../operator-handbook.md`](../operator-handbook.md): how to operate the app, plus the troubleshooting table

Those two guides remain the in-app Help sources and are not changed by this material.
If a deck and a source disagree, the source wins. Update the deck.

## Screenshots

The decks use rendered UI panels rebuilt from the production interface. Every label,
option and sample report on them is verbatim from `app.tac-to-iwxxm.com`, and the title
slide of each deck states that they are renderings rather than captures. Replacing one
with a real screenshot is a drop-in swap. See [`SCREENSHOTS.md`](./SCREENSHOTS.md) for
the filenames and the scrubbing rules.

Per the repository's figure policy, production screenshots are **not** committed here,
so the built `.pptx` files live outside the repo. Keep them wherever the facilitator
distributes beta material.

## Before you present

- Confirm the Service's focal point, and name them on the two-week plan slide if you can.
- Confirm the profile and IWXXM version that Service expects, so the options slide
  matches what testers will see.
- Confirm whether automated ingest applies at the site you are briefing, and drop that
  slide if it does not.
- Have the representative METAR / SPECI / TAF / SIGMET set and the Test Log to hand.

## Known discrepancy to resolve

The Testing and Evaluation Guide describes a **two-week** testing period but sets
submission at the **end of Week 3**. The decks follow the guide: two weeks of testing,
submission at the end of Week 3, with the intervening week for the focal point to
collate. Confirm that is the intent before the decks go out.
