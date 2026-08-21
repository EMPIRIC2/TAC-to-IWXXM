# TAC → IWXXM — Operator handbook

Short manual for meteorological operators and partners who use the converter day to day.
Start with the [Operator one-pager](operator-one-pager.md) for a single printed sheet.

## Login and access

- You can try the converter as a **guest**. Guest sessions do not keep cloud work history.
- **Sign in** when you need saved work sessions, longer history, or site features that
  require an account.
- Use the email and password issued by your organisation. If sign-in fails, check that
  you are on the correct site URL and that caps lock is off; then contact your local
  IT or MET systems contact — do not share passwords in chat or email.

## Convert and validate

1. Paste TAC or upload a file / select samples.
2. Set the **IWXXM version** and other conversion options your procedure requires.
3. Run **Convert**. Review lint messages on the TAC and the IWXXM result card.
4. Run **Validate** on the IWXXM before you treat the file as ready to share.
5. **Download** the `.xml` and store it per local SOPs.

**Soft preview** (live decode / sketch while editing) is advisory only. Official
products come from Convert (+ Validate), not from the preview alone.

## Quality metrics

The **Quality metrics** tab browses official WMO IWXXM example products and shows how
the converter’s output compares (match chip, residuals, lint, and validate summaries).

1. Open **Quality metrics** in the app shell.
2. Filter or scan the list; open a row to open a **detail** page for that example.
3. Review Official vs Converted XML and the unified diff. Equal (unchanged) regions may
   be collapsed — expand a hunk or expand all when you need full context.
4. Use Validate on your own conversions for operational readiness; Quality metrics is for
   corpus parity and operator training.

Staging URL shape: `/quality` (list) and `/quality/<example-id>` (detail).

## Work history

- When signed in, recent sessions appear in the work-history sidebar / history page.
- Open a past session to restore TAC and prior outputs for rework.
- Guests: use download promptly; clearing the browser may remove local drafts.
- Privacy settings (footer) control optional local storage — review them if you share a workstation.

## Dissemination destinations (high level)

Depending on your deployment, the UI may offer destinations such as databases or
message pathways after convert. Use only destinations your organisation has configured
and approved. If destinations are not shown, download XML and use your normal
dissemination tools. Never paste secret connection strings into shared tickets or chat.

## Automated ingest — do not rely on paste alone

When your site runs **automated near-real-time ingest** (poller / worker feeding the
store), treat that pipeline as the primary path for routine traffic. Manual paste and
convert remain available for ad-hoc fixes, training, and recovery — but **do not rely
on manual updates alone** for continuous operations if ingest is available. Confirm
with your systems contact whether ingest is active for your centre.

## Troubleshooting

| Symptom | What to try |
|--------|-------------|
| Convert fails or empty result | Check TAC terminator (`=`), product type, and station groups; fix lint errors first. |
| Validation red | Read the validation messages; fix TAC or confirm the IWXXM version matches your schema expectation. |
| Soft preview disagrees with Convert | Trust Convert/Validate; preview can lag or simplify edge cases. |
| Cannot sign in | Confirm URL, account, and network; reset password only via the approved flow. |
| History empty | Sign in; check privacy settings; confirm you are not in guest mode. |
| Destinations missing | Likely disabled for your site — use download + local channels. |
| Quality metrics empty / error | Confirm network to the API; retry; note the example id if a single row fails. |
| Diff hard to read | Expand collapsed sections; scroll Official/Converted panes; try another stem. |
| Slow or timeout | Retry once; if persistent, note the time and product and contact support. |

## Where to get help

- In-app **Help** opens the one-pager.
- This handbook for day-to-day procedures.
- Local MET/IT support for accounts, network, and approved dissemination paths.
