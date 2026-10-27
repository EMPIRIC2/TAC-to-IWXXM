# TAC → IWXXM — Operator one-pager

Print this page (one sheet). For more detail, see the [Operator handbook](operator-handbook.md).

## What this app does

Turn Traditional Alphanumeric Code (METAR, SPECI, TAF, and related products) into
IWXXM XML you can download, validate, and (when your site enables it) send onward.

## Five steps

1. **Open the converter** in your browser (guest mode works for a quick try; sign in to save history).
2. **Paste or upload** TAC text (or pick a sample). Choose the **IWXXM version** in the conversion options before you convert.
3. **Convert** — the app builds IWXXM XML. Watch the result card and any lint messages on the TAC.
4. **Validate** (recommended) — run IWXXM validation so schema/rule problems show before you share the file.
5. **Download** the `.xml` output. Keep a copy with your usual operational records.

## Soft preview (plain language)

While you type or edit TAC, the workbench may show a **soft preview**: a best-effort
decode and IWXXM sketch that updates as you go. It is for guidance only; it is **not**
the official converted product. Soft preview never means “ready to publish.” Always use
**Convert**, then **Validate IWXXM** on the **XML output** (not the original TAC), for
the file you will archive or distribute.

## Paste tips

- You can paste a WMO abbreviated heading above the report (for example
  `SAXX31 TNCM 081200` before a METAR, or `FTXX31 …` before a TAF); the converter
  strips it when it can.
- **Validate IWXXM** needs XML that starts with `<`. If you paste TAC there, the app
  asks you to convert first.
- Result status **Needs attention** / **Do not publish** means do not distribute that
  file until you fix the listed problems.

## Version

Pick the IWXXM release line your centre or partner expects (for example a recent WMO
line). If you are unsure, ask your aviation MET supervisor before changing the default.

## Dissemination (when available)

Some deployments offer send/upload destinations after convert. If that panel is hidden
or disabled at your site, download the XML and use your organisation’s normal channels.

## Need more?

Open **Help** in the app header, or read the [Operator handbook](operator-handbook.md)
for login, work history, ingest, and troubleshooting.
