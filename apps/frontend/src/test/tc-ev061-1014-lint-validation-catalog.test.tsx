/**
 * T5.1 / TC-EV061-1014 — Lint & validation catalog tab (#1014).
 *
 * Spec: docs/test-plan.md TC-EV061-1014-001..004; UJ-068; F7.v;
 * [Corpus: product §F7] [Corpus: journeys] [Corpus: tests]
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { findInternalDocRefs } from '@/utils/internalDocRefGuard';

const fetchLintIssueCatalog = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    issues: [
      {
        code: 'MISSING_TERMINATOR',
        severity: 'info',
        message_template: "Reports in bulletins end with '='",
        product: null,
        tags: ['terminator', 'metar'],
        family: 'lint',
        source_id: 'icao-annex-3',
        source_url:
          'https://store.icao.int/en/annex-3-meteorological-service-for-international-air-navigation-1',
        source_attribution:
          'icao-annex-3 — https://store.icao.int/en/annex-3-meteorological-service-for-international-air-navigation-1',
        source_type: 'tier2',
        status: 'verified',
        last_verified: '2026-08-18',
        semantic_identifier: null,
        replacement_url: null,
      },
      {
        code: 'XML_SCHEMA',
        severity: 'error',
        message_template: 'IWXXM document must validate against the pinned XSD schema',
        product: null,
        tags: ['xsd', 'iwxxm'],
        family: 'iwxxm',
        source_id: 'wmo-im-iwxxm',
        source_url: 'https://github.com/wmo-im/iwxxm',
        source_attribution: 'wmo-im-iwxxm — https://github.com/wmo-im/iwxxm',
        source_type: 'tier1',
        status: 'verified',
        last_verified: '2026-08-18',
        semantic_identifier: null,
        replacement_url: null,
      },
    ],
  }),
);

vi.mock('@/utils/api', () => ({
  fetchLintIssueCatalog: (...args: unknown[]) => fetchLintIssueCatalog(...args),
}));

vi.mock('../app/components/FileConverter', () => ({
  FileConverter: () => <div data-testid="file-converter" />,
}));

vi.mock('../app/components/MyMetarsPage', () => ({
  MyMetarsPage: () => <div data-testid="history-view" />,
}));

vi.mock('../app/components/QualityMetricsPage', () => ({
  QualityMetricsPage: () => <div data-testid="quality-metrics-page" />,
}));

vi.mock('../app/components/auth/Login', () => ({
  Login: () => <div data-testid="login-view" />,
}));

vi.mock('../app/components/auth/Register', () => ({
  Register: () => <div data-testid="register-view" />,
}));

vi.mock('../app/components/auth/EmailVerification', () => ({
  EmailVerification: () => <div data-testid="verify-view" />,
}));

vi.mock('../app/components/auth/AuthCallback', () => ({
  AuthCallback: () => <div data-testid="callback-view" />,
}));

vi.mock('../app/components/auth/PasswordReset', () => ({
  PasswordReset: () => <div data-testid="reset-view" />,
}));

vi.mock('@/utils/authService', () => ({
  getAccessToken: vi.fn(() => null),
  isLoggedIn: vi.fn(() => false),
  logout: vi.fn(),
}));

vi.mock('@/utils/localWorkSessionStore', () => ({
  listLocalWorkSessions: vi.fn().mockResolvedValue({
    items: [],
    total: 0,
    page: 1,
    limit: 20,
  }),
  migrateGuestSessionStorageToIndexedDb: vi.fn().mockResolvedValue({
    migrated: false,
    sessionId: null,
  }),
}));

vi.mock('@/utils/guestConverterState', () => ({
  readGuestConverterState: vi.fn(() => null),
  clearGuestConverterState: vi.fn(),
}));

vi.mock('@/utils/autoUploadLocalDrafts', () => ({
  autoUploadEligibleLocalDrafts: vi.fn().mockResolvedValue({ uploaded: 0, errors: [] }),
}));

vi.mock('@/utils/workSessionApi', () => ({
  listWorkSessions: vi
    .fn()
    .mockResolvedValue({ items: [], total: 0, page: 1, limit: 20 }),
}));

vi.mock('../app/components/ThemeProvider', () => ({
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock('../app/components/ui/sonner', () => ({
  Toaster: () => null,
}));

vi.mock('sonner', () => ({
  toast: { error: vi.fn(), success: vi.fn(), info: vi.fn() },
}));

import App from '../app/App';

describe('T5.1 / TC-EV061-1014: Lint & validation catalog', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.onrender.com');
  });

  it('opens Lint & validation catalog via primary shell nav (TC-EV061-1014-001)', async () => {
    const user = userEvent.setup();
    render(<App />);

    expect(screen.getByTestId('app-shell-nav')).toBeInTheDocument();
    const catalogTab = screen.getByTestId('shell-nav-catalog');
    expect(catalogTab).toHaveTextContent(/Lint & validation catalog/i);

    await user.click(catalogTab);
    expect(screen.getByTestId('lint-validation-catalog-page')).toBeInTheDocument();
    expect(screen.queryByTestId('file-converter')).not.toBeInTheDocument();
    expect(catalogTab).toHaveAttribute('aria-selected', 'true');
  });

  it('lists code, description, level, and clickable source hrefs (TC-EV061-1014-002)', async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByTestId('shell-nav-catalog'));
    const page = await screen.findByTestId('lint-validation-catalog-page');
    const list = within(page).getByTestId('lint-validation-catalog-list');

    const lintRow = within(list).getByTestId(
      'lint-validation-catalog-entry-MISSING_TERMINATOR',
    );
    expect(lintRow).toHaveTextContent('MISSING_TERMINATOR');
    expect(lintRow).toHaveTextContent(/info/i);
    expect(lintRow).toHaveTextContent("Reports in bulletins end with '='");
    const lintLink = within(lintRow).getByRole('link');
    expect(lintLink).toHaveAttribute(
      'href',
      'https://store.icao.int/en/annex-3-meteorological-service-for-international-air-navigation-1',
    );

    const iwxxmRow = within(list).getByTestId(
      'lint-validation-catalog-entry-XML_SCHEMA',
    );
    expect(iwxxmRow).toHaveTextContent('XML_SCHEMA');
    expect(iwxxmRow).toHaveTextContent(/error/i);
    expect(iwxxmRow).toHaveTextContent(/XSD schema/i);
    const iwxxmLink = within(iwxxmRow).getByRole('link');
    expect(iwxxmLink).toHaveAttribute('href', 'https://github.com/wmo-im/iwxxm');
  });

  it('keeps catalog page copy free of planning ids (TC-EV061-1014-004)', async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByTestId('shell-nav-catalog'));
    const page = await screen.findByTestId('lint-validation-catalog-page');
    const text = page.textContent ?? '';
    expect(findInternalDocRefs(text)).toEqual([]);
  });
});
