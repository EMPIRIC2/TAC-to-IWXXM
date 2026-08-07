# Build walkthrough — assemble the `.pptx`

PowerPoint-first steps; Keynote / Google Slides equivalents in parentheses.
Work from [slide-outline.md](./slide-outline.md) and [image-pointers.md](./image-pointers.md).

**Do not** commit the finished `.pptx` to git unless explicitly requested.

---

## 0. Setup (5 minutes)

1. Open **PowerPoint** → Blank Presentation (Keynote: File → New; Slides: Blank).  
2. Set slide size: **Widescreen 16:9** (Design → Slide Size).  
3. Apply a simple theme (one accent color). Avoid purple-on-white cliché if you care about branding.  
4. View → **Notes** (enable speaker notes).  
5. Optional footer master: `Pin: IWXXM v2025-2 · Sources briefing`  
6. Keep this pack open side-by-side with the deck.

**Checklist before any content:** citation policy — titles + URLs only; no Annex 3 body text.

---

## Batch A — Slides 1–4 (start here in coaching)

### Slide 1 — Title

1. Title placeholder → paste title from outline.  
2. Subtitle → pin line.  
3. Notes → paste speaker notes.  
4. Insert org logo if any (Insert → Pictures).

### Slide 2 — Why IWXXM

1. New slide → Title and Content.  
2. Paste bullets.  
3. Insert → Shapes: two rectangles “TAC” and “IWXXM”, arrow between.  
4. Notes: dual-obligation cite + “informative PPT-02” caveat.

### Slide 3 — Standards map

1. Paste bullets (keep paywall labels).  
2. Optional: Insert screenshot of https://schemas.wmo.int/iwxxm/2025-2/ (public landing).  
3. Notes: point to RULE_SOURCE_URLS.md path for Q&A.

### Slide 4 — Architecture

1. Prefer **SmartArt** Process/Hierarchy or freeform boxes matching image-pointers mermaid.  
2. Labels exactly: `apps/frontend`, `apps/backend`, three packages, `vendor/schemas`.  
3. Notes: F21 public convert / F31 optional Auth.

**Pause:** review Batch A for invented claims (none should appear).

---

## Batch B — Slides 5–8

### Slide 5 — Pipeline

1. SmartArt **Basic Process** with 7 chevrons, or numbered list.  
2. Text from domain README stage names.  
3. Notes: stages are separate concerns.

### Slide 6 — Vendor pins

1. Table 2×5: Bundle | Pin.  
2. Or screenshot `vendor/manifest.json` (tag fields only).  
3. Notes: conflict → defer to pin; translation suite informative.

### Slide 7 — Operator UI

1. Paste F7/F9/F10 bullets.  
2. Insert 1–2 **local** screenshots (image-pointers §UI).  
3. Caption: “Local non-deployed preview”.  
4. Notes: runbook path for operators.

### Slide 8 — Provenance

1. Three boxes: Dig → ISSUE_CATALOG → Lint UI.  
2. Notes: EV-035 / EV-040; gap/paywall labels.

**Pause:** confirm no copyrighted PDF pages pasted.

---

## Batch C — Slides 9–12

### Slide 9 — Access friction

1. Insert → Table (copy from outline).  
2. Emphasize paywall row visually (e.g. italic “purchase”).

### Slide 10 — PPT-02

1. Bullets from outline.  
2. Optional figure: personal extract from `.local/.../slide-images/` **or** open official download and snip slides 6–7 only.  
3. Notes: full attribution paragraph from image-pointers.  
4. On-slide badge: **INFORMATIVE — not SoT**.

### Slide 11 — Software stack

1. Short bullet list from outline (not full inventory).  
2. Notes: dependency-inventory.md for detail; ADR-014 GIFTs removed.

### Slide 12 — Bibliography

1. Paste short URL list.  
2. Handout: print or link `bibliography.md`.  
3. Closing line: “Operator day-to-day: docs/ops/operator-ui-runbook.md”.

---

## Final checklist

- [ ] Every slide has speaker notes with at least one corpus/path cite or landing URL  
- [ ] Paywalled sources labeled  
- [ ] PPT-02 (if used) labeled informative  
- [ ] Pin **v2025-2** appears on title and/or footer  
- [ ] No Annex 3 / MoC multi-paragraph paste  
- [ ] UI shots labeled non-deployed (if present)  
- [ ] File saved outside repo (e.g. `~/Documents/TAC-to-IWXXM-sources-briefing.pptx`)  
- [ ] Matches [bibliography.md](./bibliography.md) landings

---

## Coaching cadence (chat)

When walking through with an agent:

1. Complete **Batch A** → reply “Batch A done” (or note blockers).  
2. Then Batch B → “Batch B done”.  
3. Then Batch C → final checklist.  

Equivalents: Keynote **Presenter Notes**; Google Slides **Speaker notes** panel.
