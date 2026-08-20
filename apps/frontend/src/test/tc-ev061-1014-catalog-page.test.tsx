/**
 * LintValidationCatalogPage unit coverage (#1014 / TC-EV061-1014).
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LintValidationCatalogPage } from '../app/components/LintValidationCatalogPage';

const fetchLintIssueCatalog = vi.hoisted(() => vi.fn());

vi.mock('@/utils/api', () => ({
  fetchLintIssueCatalog: (...args: unknown[]) => fetchLintIssueCatalog(...args),
}));

const BASE_ISSUES = [
  {
    code: 'MISSING_TERMINATOR',
    severity: 'info',
    message_template: "Reports in bulletins end with '='",
    product: null,
    tags: ['terminator'],
    family: 'lint',
    source_url:
      'https://store.icao.int/en/annex-3-meteorological-service-for-international-air-navigation-1',
    status: 'verified',
  },
  {
    code: 'XML_SCHEMA',
    severity: 'error',
    message_template: 'IWXXM document must validate against the pinned XSD schema',
    product: null,
    tags: ['xsd'],
    family: 'iwxxm',
    source_url: 'https://github.com/wmo-im/iwxxm',
    status: 'verified',
  },
  {
    code: 'VENDOR_ONLY',
    severity: 'warning',
    message_template: 'Vendor pin reference (not a web landing)',
    product: null,
    tags: ['ahl'],
    family: 'lint',
    source_url: 'vendor:documentation/webpages/AHL.asciidoc',
    status: 'semantic_only',
  },
];

describe('LintValidationCatalogPage', () => {
  beforeEach(() => {
    fetchLintIssueCatalog.mockReset();
    fetchLintIssueCatalog.mockResolvedValue({ issues: BASE_ISSUES });
  });

  it('renders verified links and plain text for semantic-only sources', async () => {
    render(<LintValidationCatalogPage />);
    const list = await screen.findByTestId('lint-validation-catalog-list');

    const verified = within(list).getByTestId(
      'lint-validation-catalog-entry-XML_SCHEMA',
    );
    expect(within(verified).getByRole('link')).toHaveAttribute(
      'href',
      'https://github.com/wmo-im/iwxxm',
    );

    const semantic = within(list).getByTestId(
      'lint-validation-catalog-entry-VENDOR_ONLY',
    );
    expect(within(semantic).queryByRole('link')).not.toBeInTheDocument();
    expect(semantic).toHaveTextContent('vendor:documentation/webpages/AHL.asciidoc');
  });

  it('filters by family via the select', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    await screen.findByTestId('lint-validation-catalog-list');

    fetchLintIssueCatalog.mockResolvedValueOnce({
      issues: BASE_ISSUES.filter((row) => row.family === 'iwxxm'),
    });
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-family-filter'),
      'iwxxm',
    );

    expect(fetchLintIssueCatalog).toHaveBeenLastCalledWith({ family: 'iwxxm' });
    const list = await screen.findByTestId('lint-validation-catalog-list');
    expect(
      within(list).getByTestId('lint-validation-catalog-entry-XML_SCHEMA'),
    ).toBeInTheDocument();
    expect(
      within(list).queryByTestId('lint-validation-catalog-entry-MISSING_TERMINATOR'),
    ).not.toBeInTheDocument();
  });

  it('shows empty and error states', async () => {
    fetchLintIssueCatalog.mockResolvedValueOnce({ issues: [] });
    const { unmount } = render(<LintValidationCatalogPage />);
    expect(await screen.findByText(/No catalog entries/i)).toBeInTheDocument();
    unmount();

    fetchLintIssueCatalog.mockRejectedValueOnce(new Error('catalog down'));
    const { unmount: unmount2 } = render(<LintValidationCatalogPage />);
    expect(await screen.findByRole('alert')).toHaveTextContent('catalog down');
    unmount2();

    fetchLintIssueCatalog.mockRejectedValueOnce('offline');
    render(<LintValidationCatalogPage />);
    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Failed to load catalog',
    );
  });

  it('shows a dash when source_url is absent', async () => {
    fetchLintIssueCatalog.mockResolvedValueOnce({
      issues: [
        {
          code: 'NO_SOURCE',
          severity: 'info',
          message_template: 'No source URL',
          family: 'lint',
          source_url: null,
          status: 'verified',
        },
        {
          code: 'HTTP_NO_STATUS',
          severity: 'info',
          message_template: 'Verified landing without status field',
          family: 'lint',
          source_url: 'https://codes.wmo.int/',
        },
      ],
    });
    render(<LintValidationCatalogPage />);
    const row = await screen.findByTestId('lint-validation-catalog-entry-NO_SOURCE');
    expect(row).toHaveTextContent('—');
    const httpRow = await screen.findByTestId(
      'lint-validation-catalog-entry-HTTP_NO_STATUS',
    );
    expect(within(httpRow).getByRole('link')).toHaveAttribute(
      'href',
      'https://codes.wmo.int/',
    );
  });

  it('tolerates missing issues array, family, and code', async () => {
    fetchLintIssueCatalog.mockResolvedValueOnce({ issues: undefined });
    const { unmount } = render(<LintValidationCatalogPage />);
    expect(await screen.findByText(/No catalog entries/i)).toBeInTheDocument();
    unmount();

    fetchLintIssueCatalog.mockResolvedValueOnce({
      issues: [
        {
          severity: 'info',
          message_template: 'Missing code/family',
          source_url: 'https://example.invalid/landing',
          status: 'verified',
        },
        {
          code: 'B_SECOND',
          severity: 'info',
          message_template: 'Sort after',
          family: 'lint',
          source_url: 'https://example.invalid/b',
          status: 'verified',
        },
      ],
    });
    render(<LintValidationCatalogPage />);
    const list = await screen.findByTestId('lint-validation-catalog-list');
    expect(list.textContent).toMatch(/Missing code\/family/);
    expect(
      within(list).getByTestId('lint-validation-catalog-entry-B_SECOND'),
    ).toBeInTheDocument();
  });
});
