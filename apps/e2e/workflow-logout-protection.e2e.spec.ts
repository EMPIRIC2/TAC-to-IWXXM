/**
 * Logout protection workflow — **retired F21** (no Auth / logout chrome).
 */
import { test } from '@playwright/test';

test.describe('Workflow: Logout Protection', () => {
  test('logout options are visible and this-device logout returns user to login form', async () => {
    test.skip(true, 'Retired F21 — operator Auth / logout removed (TC-F21-auth-gone)');
  });
});
