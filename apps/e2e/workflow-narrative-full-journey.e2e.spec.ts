/**
 * Narrative full journey — **retired F21** (login → admin → logout path gone).
 * Public convert / preferences covered by tac-file-conversion + public-app-f21-f22.
 */
import { test } from '@playwright/test';

test.describe('Workflow: Narrative Full Journey', () => {
  test('login -> preferences -> conversion -> theme -> logout', async () => {
    test.skip(
      true,
      'Retired F21 — Auth/admin/logout narrative removed (TC-F21-auth-gone)',
    );
  });
});
