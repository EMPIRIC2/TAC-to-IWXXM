import { expect, test } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { loginAndOpenConverter } from './playwright-e2e-helpers';

const DEFAULT_TAC_RELATIVE_PATH = 'data/iwxxm-translation/Amd79-80-2023/metar';
const REQUIRE_TAC_FIXTURES =
  process.env.PLAYWRIGHT_REQUIRE_TAC_FIXTURES === '1' || process.env.CI === 'true';

function resolveTacFilesDir(): string | null {
  const configured = process.env.PLAYWRIGHT_TAC_FIXTURES_DIR;
  if (configured) {
    if (!fs.existsSync(configured)) {
      throw new Error(
        `PLAYWRIGHT_TAC_FIXTURES_DIR is set but does not exist: ${configured}`,
      );
    }
    return configured;
  }

  const candidateFromRepoRoot = path.resolve(process.cwd(), DEFAULT_TAC_RELATIVE_PATH);
  if (fs.existsSync(candidateFromRepoRoot)) {
    return candidateFromRepoRoot;
  }

  const candidateFromFrontendCwd = path.resolve(
    process.cwd(),
    '..',
    DEFAULT_TAC_RELATIVE_PATH,
  );
  if (fs.existsSync(candidateFromFrontendCwd)) {
    return candidateFromFrontendCwd;
  }

  if (REQUIRE_TAC_FIXTURES) {
    throw new Error(
      [
        'No TAC fixtures directory found for Playwright upload tests.',
        `Checked: ${candidateFromRepoRoot}`,
        `Checked: ${candidateFromFrontendCwd}`,
        'Set PLAYWRIGHT_TAC_FIXTURES_DIR or disable strict fixture requirement with PLAYWRIGHT_REQUIRE_TAC_FIXTURES=0 for local runs.',
      ].join(' '),
    );
  }

  return null;
}

type TacFixture = {
  content: string;
  name: string;
  path: string;
};

function getTacFiles(): TacFixture[] {
  const tacFilesDir = resolveTacFilesDir();
  if (!tacFilesDir) {
    return [];
  }

  return fs
    .readdirSync(tacFilesDir)
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
      page.getByRole('button', { name: /Upload 0 converted files to database/i }),
    ).toBeDisabled();
  });

  test('single TAC file can be converted and sent with one click', async ({ page }) => {
    test.skip(
      true,
      'EV-042: Convert&Send hidden (OPERATOR_DISSEMINATION_DESTINATIONS_ENABLED=false); restore #898',
    );
    const tacFiles = getTacFiles();
    test.skip(
      tacFiles.length === 0,
      'No TAC fixture files available for upload E2E coverage.',
    );

    const testFile = tacFiles[0];
    await loginAndOpenConverter(page);

    await page.route('**/functions/v1/**/database/upload', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Files converted and sent successfully',
          results: [{ recordId: 'playwright-convert-send-id' }],
        }),
      });
    });

    await page.locator('input[type="file"]').setInputFiles(testFile.path);
    await page.getByTestId('convert-and-send-button').click();

    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      { timeout: 10000 },
    );
    await expect(page.locator('pre').first()).toContainText(/iwxxm|metar:/i);
    await expect(page.getByText(/Files converted and sent successfully/i)).toBeVisible({
      timeout: 10000,
    });
  });

  test('single TAC file can be converted and uploaded', async ({ page }) => {
    const tacFiles = getTacFiles();
    test.skip(
      tacFiles.length === 0,
      'No TAC fixture files available for upload E2E coverage.',
    );

    const testFile = tacFiles[0];
    await loginAndOpenConverter(page);

    await page.route('**/functions/v1/**/database/upload', async (route) => {
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
    await page.getByTestId('convert-button').click();

    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      { timeout: 10000 },
    );
    await expect(page.locator('pre').first()).toContainText(/iwxxm|metar:/i);

    await page
      .getByRole('button', { name: /Upload 1 converted files to database/i })
      .click();
    await page.getByRole('radio', { name: /Store as IWXXM XML only/i }).check();
    await page.getByRole('button', { name: /Upload files to database/i }).click();

    await expect(page.getByText(/Files uploaded successfully!/i)).toBeVisible({
      timeout: 10000,
    });
  });

  test('multiple TAC files can be queued and converted', async ({ page }) => {
    const tacFiles = getTacFiles();
    test.skip(
      tacFiles.length < 2,
      'At least two TAC fixture files are required for multi-file upload coverage.',
    );

    await loginAndOpenConverter(page);

    await page
      .locator('input[type="file"]')
      .setInputFiles(tacFiles.slice(0, 2).map((file) => file.path));
    await page.getByTestId('convert-button').click();

    await expect(page.getByRole('region', { name: /conversion results/i })).toBeVisible(
      { timeout: 10000 },
    );
    const resultsRegion = page.getByRole('region', { name: /conversion results/i });
    // Each converted file renders Source TAC + IWXXM blocks (2 <pre> per result).
    await expect(resultsRegion.locator('pre')).toHaveCount(4);
    await expect(
      page.getByRole('button', { name: /Upload 2 converted files to database/i }),
    ).toBeEnabled();
  });

  test('invalid manual TAC shows an error state', async ({ page }) => {
    await loginAndOpenConverter(page);

    await page.getByLabel(/Enter METAR data manually/i).fill('INVALID TAC FORMAT');
    await page.getByTestId('convert-button').click();

    await expect(page.getByText(/Conversion Error/i).first()).toBeVisible({
      timeout: 10000,
    });
  });
});
