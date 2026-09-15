# UI figures in the tester decks

Both decks currently use **rendered UI panels**, not photographic screenshots. Each
panel was rebuilt from the production interface: every tab name, button label, option
value, helper sentence and sample report on them was read off `app.tac-to-iwxxm.com`
and is reproduced verbatim. The title slide of each deck says so.

They were rendered rather than captured because `app.tac-to-iwxxm.com` is refused by
the organisation's egress policy from the build environment, so the host could be read
through a browser but not captured to a file.

**Replacing a panel with a real capture is a drop-in swap.** Save a capture over the
matching filename below and rebuild; anything not replaced keeps its rendered panel.
One figure, the dissemination drawer, has no panel at all, because its contents are
site-specific; that slide shows a labelled note instead.

## How to capture

1. Open **https://app.tac-to-iwxxm.com** in a clean browser window, with no other tabs
   visible, no bookmarks bar, and signed **out** unless a shot says otherwise.
2. Capture just the app area, not the whole desktop (macOS: `⌘⇧4`, then drag).
3. Save each file with the **exact filename** below into the capture folder.
4. Scrub before you save: no personal email address, no account name, and no TAC that
   is not a published sample. The demo examples in the Examples picker are safe.

Capture folder on this machine: `~/Desktop/beta-deck-shots/`


## If you swap only a few

These five appear most often, so replacing them changes the most slides:

1. `01-converter-shell.png`: used on 3 slides
2. `06-convert-result.png`: used on 3 slides
3. `05-soft-preview.png`: used on 2 slides, and it is the deck's key warning
4. `02-guest-banner.png`: used on 2 slides
5. `08-history.png`: the guest-vs-signed-in slide

You can also drag the files straight into the chat instead of saving them to the
folder. Either way works.

## Filenames

| Filename | What to capture | Used on |
|---|---|---|
| `01-converter-shell.png` | Whole Convert view as a guest: tab row, title, `HELP` / `PREFERENCES` / `Theme` / `SIGN IN` | Title slides, Tour of the shell |
| `02-guest-banner.png` | The "Progress may be lost without signing in" bar plus the privacy notice below it | Access slides |
| `03-input-modes.png` | `Manual TAC Input` with the `TAC report` / `AHL bulletin` / `IWXXM COLLECT` / `Validate IWXXM` row, plus Product type, Profile and Exchange profile | Options slide |
| `04-decode-panel.png` | The `Decode` panel: plain-language paragraph and the CODE / EXPLANATION table | Decode slide |
| `05-soft-preview.png` | The `IWXXM preview` panel with the `Soft-preview` toggle and its caption visible | Soft-preview slides (both decks) |
| `06-convert-result.png` | After Convert: the `Conversion / validation log` showing Issues and Results with the download link | Convert, Validate, Five-steps slides |
| `07-action-bar.png` | The button row: `NEW TAC` `CONVERT` `CONVERT&SEND` `UPLOAD TO DATABASE` `DISSEMINATE` `DOWNLOAD ZIP` `CLEAR` | Five steps, Download |
| `08-history.png` | History tab: `My METARs`, the `Local history` label, the status filters | Work history |
| `09-quality-metrics.png` | Quality metrics list with the count tiles and a few example rows | Quality metrics |
| `10-quality-detail.png` | One Quality metrics example opened: Official / Converted panes and the diff | Quality metrics |
| `11-upload-zone.png` | The drop zone: "Drop TAC files or select" with `SELECT FILES` / `FOLDER` / `ZIP` | Three ways in |
| `12-privacy-settings.png` | The header close-up (`HELP`, `PREFERENCES`, Theme, `SIGN IN`) or the Privacy settings panel | Where to get help |

## Optional: only if the panel is enabled at your site

| Filename | What to capture | Used on |
|---|---|---|
| `13-dissemination-drawer.png` | The dissemination drawer, with any destination names or addresses blanked out | Dissemination |

If dissemination is not enabled, leave this one out; the slide still reads correctly
with its placeholder, and the copy already says the panel may be hidden.

## Rebuilding

Drop the files into the capture folder and rebuild. Frames are sized from each image's
own aspect ratio, so a real capture of a different shape re-flows rather than stretching.
