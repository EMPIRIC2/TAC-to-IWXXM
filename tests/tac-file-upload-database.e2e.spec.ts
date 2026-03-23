import { expect, test } from '../frontend/node_modules/@playwright/test';
import * as fs from 'fs';
import { loginAndOpenConverter } from './playwright-e2e-helpers';

const tacFilesDir = '/root/metar-to-IWXXM/data/iwxxm-translation/Amd79-80-2023/metar';

type TacFixture = {
  content: string;
  name: string;
  path: string;
};

function getTacFiles(): TacFixture[] {
  if (!fs.existsSync(tacFilesDir)) {
    return [];
  }

  return fs.readdirSync(tacFilesDir)
    .filter((fileName) => fileName.endsWith('.tac'))
    .slice(0, 3)
    .map((fileName) => ({
      content: fs.readFileSync(`${tacFilesDir}/${fileName}`, 'utf-8').trim(),
      name: fileName,
      path: `${tacFilesDir}/${fileName}`,
    }));
}

test.describe('TAC File Upload to Database', () => {
  test('upload button stays disabled before conversion', async ({ page }) => {
    await loginAndOpenConverter(page);

    await expect(
      page.getByRole('button', { name: /Upload 0 converted files to database/i })
    ).toBeDisabled();
  });

  test('single TAC file can be converted and uploaded', async ({ page }) => {
    const tacFiles = getTacFiles();
    test.skip(tacFiles.length === 0, 'No TAC fixture files available for upload E2E coverage.');

    const testFile = tacFiles[0];
    await loginAndOpenConverter(page);

    await page.route('**/functions/v1/make-server-2e3cda33/database/upload', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Files uploaded successfully',
          results: [
            {
              recordId: 'playwright-record-id',
            },
          ],
        }),
      });
    });

    await page.locator('input[type="file"]').setInputFiles(testFile.path);
    await page.getByRole('button', { name: /Convert METAR files to IWXXM XML/i }).click();

    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible({ timeout: 10000 });
    await expect(page.locator('pre').first()).toContainText(/iwxxm|metar:/i);

    await page.getByRole('button', { name: /Upload 1 converted files to database/i }).click();
    await page.getByRole('radio', { name: /Store as IWXXM XML only/i }).check();
    await page.getByRole('button', { name: /Upload files to database/i }).click();

    await expect(page.getByText(/Files uploaded successfully!/i)).toBeVisible({ timeout: 10000 });
  });

  test('multiple TAC files can be queued and converted', async ({ page }) => {
    const tacFiles = getTacFiles();
    test.skip(tacFiles.length < 2, 'At least two TAC fixture files are required for multi-file upload coverage.');

    await loginAndOpenConverter(page);

    await page.locator('input[type="file"]').setInputFiles(tacFiles.slice(0, 2).map((file) => file.path));
    await page.getByRole('button', { name: /Convert METAR files to IWXXM XML/i }).click();

    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible({ timeout: 10000 });
    await expect(page.locator('pre')).toHaveCount(2);
    await expect(page.getByRole('button', { name: /Upload 2 converted files to database/i })).toBeEnabled();
  });

  test('invalid manual TAC shows an error state', async ({ page }) => {
    await loginAndOpenConverter(page);

    await page.getByLabel(/Enter METAR data manually/i).fill('INVALID TAC FORMAT');
    await page.getByRole('button', { name: /Convert METAR files to IWXXM XML/i }).click();

    await expect(page.getByText(/Conversion Error/i).first()).toBeVisible({ timeout: 10000 });
  });
});