/**
 * Auth readiness workflow — **retired F21** (operator Auth removed).
 * Coverage moved to auth.e2e.spec.ts / public-app-f21-f22.e2e.spec.ts (TC-F21-auth-gone).
 */
import { test } from '@playwright/test';

test.describe('Workflow: Auth readiness', () => {
  test('startup and login reach converter (no admin dashboard)', async () => {
    test.skip(true, 'Retired F21 — operator Auth UX removed (TC-F21-auth-gone)');
  });
});
