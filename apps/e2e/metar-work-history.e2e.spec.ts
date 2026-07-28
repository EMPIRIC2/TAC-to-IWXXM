/**
 * UJ-004 — METAR work history via IndexedDB (F5 / F7.h / F21).
 *
 * Spec: docs/test-plan.md TC-004; S023 / EV-017 / T7.1.
 * No `/api/v1/work-sessions` — local store only.
 */
import { expect, test } from '@playwright/test';
import { openPublicConverter, seedLocalWorkSession } from './playwright-e2e-helpers';

const SAMPLE_METAR =
  'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990';

test.describe('UJ-004 — METAR work history (IndexedDB)', () => {
  test('auto-save indicator appears while typing (no work-sessions API)', async ({
    page,
  }) => {
    const sessionCalls: string[] = [];
    await page.route('**/api/v1/work-sessions**', async (route) => {
      sessionCalls.push(`${route.request().method()} ${route.request().url()}`);
      await route.fulfill({ status: 404, body: 'not found' });
    });

    await openPublicConverter(page);

    const manualInput = page.getByLabel(/Enter METAR data manually/i);
    await manualInput.fill(SAMPLE_METAR);

    await expect(page.getByTestId('autosave-indicator')).toContainText(/saved/i, {
      timeout: 10_000,
    });
    expect(sessionCalls).toEqual([]);
  });

  test('finished IndexedDB session disables convert buttons', async ({ page }) => {
    await page.goto('/');
    await seedLocalWorkSession(page, {
      id: 'finished-1',
      user_id: 'local',
      product: 'metar',
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
    });

    await page.reload();
    await openPublicConverter(page);

    await page.getByRole('button', { name: /KJFK finished/i }).click();

    await expect(page.getByTestId('convert-button')).toBeDisabled({ timeout: 10_000 });
    await expect(page.getByTestId('convert-and-send-button')).toBeDisabled();
    await expect(
      page.getByRole('status').filter({ hasText: /read-only/i }),
    ).toBeVisible();
  });
});
