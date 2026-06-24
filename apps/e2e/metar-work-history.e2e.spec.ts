import { expect, test } from '@playwright/test';
import { openConverterWithMockSession } from './playwright-e2e-helpers';

const SAMPLE_METAR =
  'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990';

test.describe('UJ-004 — METAR work history (mocked API)', () => {
  test('auto-save indicator appears while typing', async ({ page }) => {
    const sessionId = 'session-1';

    await page.route('**/api/v1/work-sessions**', async (route) => {
      const url = route.request().url();
      const method = route.request().method();

      if (method === 'GET' && !url.includes('/work-sessions/')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ items: [], total: 0, page: 1, limit: 20 }),
        });
        return;
      }

      if (method === 'POST') {
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: sessionId,
            user_id: 'user-1',
            status: 'draft',
            title: 'KJFK',
            manual_tac: SAMPLE_METAR,
            pending_files: [],
            converted_results: [],
            errors: [],
            issues: [],
            conversion_params: {},
            kv_upload_key: null,
            deleted_at: null,
            created_at: '2026-06-24T00:00:00Z',
            updated_at: '2026-06-24T00:00:00Z',
          }),
        });
        return;
      }

      if (method === 'PATCH') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: sessionId,
            user_id: 'user-1',
            status: 'draft',
            title: 'KJFK',
            manual_tac: SAMPLE_METAR,
            pending_files: [],
            converted_results: [],
            errors: [],
            issues: [],
            conversion_params: {},
            kv_upload_key: null,
            deleted_at: null,
            created_at: '2026-06-24T00:00:00Z',
            updated_at: '2026-06-24T00:00:01Z',
          }),
        });
        return;
      }

      await route.continue();
    });

    await openConverterWithMockSession(page);

    const manualInput = page.getByLabel(/Enter METAR data manually/i);
    await manualInput.fill(SAMPLE_METAR);

    await expect(page.getByTestId('autosave-indicator')).toBeVisible({ timeout: 8000 });
    await expect(page.getByTestId('autosave-indicator')).toContainText(/saved/i, {
      timeout: 8000,
    });
  });

  test('finished session disables convert buttons', async ({ page }) => {
    const finishedSession = {
      id: 'finished-1',
      user_id: 'user-1',
      status: 'finished',
      title: 'KJFK finished',
      manual_tac: SAMPLE_METAR,
      pending_files: [],
      converted_results: [
        {
          name: 'manual',
          tac_input: SAMPLE_METAR,
          iwxxm_xml: '<iwxxm/>',
        },
      ],
      errors: [],
      issues: [],
      conversion_params: {},
      kv_upload_key: 'kv-1',
      deleted_at: null,
      created_at: '2026-06-24T00:00:00Z',
      updated_at: '2026-06-24T00:00:00Z',
    };

    await page.route('**/api/v1/work-sessions**', async (route) => {
      const method = route.request().method();
      if (method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [finishedSession],
            total: 1,
            page: 1,
            limit: 20,
          }),
        });
        return;
      }
      await route.continue();
    });

    await openConverterWithMockSession(page);

    await page.getByRole('button', { name: /KJFK finished/i }).click();

    await expect(page.getByTestId('convert-button')).toBeDisabled({ timeout: 10000 });
    await expect(page.getByTestId('convert-and-send-button')).toBeDisabled();
    await expect(page.getByRole('status').filter({ hasText: /read-only/i })).toBeVisible();
  });
});
