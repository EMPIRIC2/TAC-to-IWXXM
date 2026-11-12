/**
 * CodeMirror TAC editor helpers for Playwright (Results/Dissemination overlays).
 */
import { expect, type Page } from '@playwright/test';

type CmDispatchView = {
  dispatch: (t: unknown) => void;
  state: { doc: { length: number } };
};

type CmTile = {
  root?: { view?: CmDispatchView };
  parent?: CmTile;
};

/** Set CodeMirror doc text via EditorView.dispatch (CM6 attaches `cmTile`). */
export async function setTacEditorText(page: Page, text: string): Promise<void> {
  const host = page.getByTestId('tac-editor').last();
  await expect(host).toBeAttached({ timeout: 15_000 });
  await host.evaluate((root, next) => {
    const content = root.querySelector('.cm-content') as
      | (HTMLElement & { cmTile?: CmTile })
      | null;
    if (!content) {
      throw new Error('TAC editor .cm-content missing');
    }
    let tile: CmTile | undefined = content.cmTile;
    while (tile && !tile.root?.view) {
      tile = tile.parent;
    }
    const view = tile?.root?.view;
    if (!view) {
      throw new Error('CodeMirror EditorView not found on .cm-content');
    }
    view.dispatch({
      changes: { from: 0, to: view.state.doc.length, insert: next },
    });
  }, text);
}

/**
 * Replace CodeMirror TAC text without OS select-all (flaky under overlays).
 */
export async function fillManualTac(page: Page, metar: string): Promise<void> {
  await setTacEditorText(page, metar);
  const content = page.getByTestId('tac-editor').last().locator('.cm-content');
  await expect
    .poll(async () => (await content.innerText()).replace(/\s+/g, ' '), {
      timeout: 10_000,
    })
    .toContain(metar.replace(/\s+/g, ' ').slice(0, 24));
  await expect(page.getByTestId('convert-empty-hero')).toHaveCount(0, {
    timeout: 15_000,
  });
}

/**
 * Apply a live TAC lint span fix (e.g. add_terminator) via the editor event.
 *
 * Console quick-fix buttons were removed with WorkbenchConsole; fixes still
 * surface on CodeMirror spans and listen for `tac-span-fix`.
 *
 * @param page - Playwright page hosting the converter.
 * @param fixCode - Lint fix id (e.g. ``add_terminator``).
 */
export async function applyTacSpanFix(page: Page, fixCode: string): Promise<void> {
  const editor = page.getByTestId('tac-editor').last();
  await expect(editor).toBeVisible();
  await editor.locator('.cm-editor').evaluate((el, code) => {
    el.dispatchEvent(
      new CustomEvent('tac-span-fix', {
        bubbles: true,
        detail: { fixCode: code },
      }),
    );
  }, fixCode);
}
