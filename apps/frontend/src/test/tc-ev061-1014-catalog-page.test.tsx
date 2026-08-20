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
    issue_type: 'structure',
    source_access: 'paywall',
    source_locator: 'ICAO Annex 3 App 5',
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
    issue_type: 'iwxxm_schema',
    source_access: 'public',
    source_locator: 'Pinned XSD schema bundle',
    source_url: 'https://github.com/wmo-im/iwxxm',
    status: 'verified',
  },
  {
    code: 'AMD_PRESENT',
    severity: 'info',
    message_template: 'AMD modifier noted',
    product: 'taf',
    tags: ['modifier'],
    family: 'lint',
    issue_type: 'presence',
    source_access: 'paywall',
    source_locator: 'App 5 / Table A5-1',
    source_url:
      'https://store.icao.int/en/annex-3-meteorological-service-for-international-air-navigation-1',
    status: 'verified',
  },
  {
    code: 'VENDOR_ONLY',
    severity: 'warning',
    message_template: 'Vendor pin reference (not a web landing)',
    product: null,
    tags: ['ahl'],
    family: 'lint',
    issue_type: 'structure',
    source_access: 'semantic_only',
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

  it('filters by issue type via API (TC-EV062-001)', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    await screen.findByTestId('lint-validation-catalog-list');

    fetchLintIssueCatalog.mockResolvedValueOnce({
      issues: BASE_ISSUES.filter((row) => row.issue_type === 'presence'),
    });
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-type-filter'),
      'presence',
    );

    expect(fetchLintIssueCatalog).toHaveBeenLastCalledWith({
      issue_type: 'presence',
    });
    const list = await screen.findByTestId('lint-validation-catalog-list');
    expect(
      within(list).getByTestId('lint-validation-catalog-entry-AMD_PRESENT'),
    ).toBeInTheDocument();
    expect(
      within(list).queryByTestId('lint-validation-catalog-entry-XML_SCHEMA'),
    ).not.toBeInTheDocument();
  });

  it('sorts by issue type client-side (TC-EV062-002)', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    const list = await screen.findByTestId('lint-validation-catalog-list');

    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-sort'),
      'issue_type',
    );

    const rows = within(list).getAllByRole('row');
    const codes = rows
      .slice(1)
      .map((row) => row.querySelector('td')?.textContent?.trim());
    expect(codes).toEqual([
      'XML_SCHEMA',
      'AMD_PRESENT',
      'MISSING_TERMINATOR',
      'VENDOR_ONLY',
    ]);
  });

  it('shows source locator and access near source column (TC-EV062-003)', async () => {
    render(<LintValidationCatalogPage />);
    const row = await screen.findByTestId('lint-validation-catalog-entry-XML_SCHEMA');
    expect(row).toHaveTextContent('Pinned XSD schema bundle');
    expect(row).toHaveTextContent(/Access: public/i);
  });

  it('filters by level client-side (TC-EV062-004)', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    await screen.findByTestId('lint-validation-catalog-list');

    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-level-filter'),
      'error',
    );
    const list = await screen.findByTestId('lint-validation-catalog-list');
    expect(
      within(list).getByTestId('lint-validation-catalog-entry-XML_SCHEMA'),
    ).toBeInTheDocument();
    expect(
      within(list).queryByTestId('lint-validation-catalog-entry-MISSING_TERMINATOR'),
    ).not.toBeInTheDocument();
  });

  it('filters by source access via API (TC-EV062-005)', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    await screen.findByTestId('lint-validation-catalog-list');

    fetchLintIssueCatalog.mockResolvedValueOnce({
      issues: BASE_ISSUES.filter((row) => row.source_access === 'public'),
    });
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-access-filter'),
      'public',
    );

    expect(fetchLintIssueCatalog).toHaveBeenLastCalledWith({
      source_access: 'public',
    });
    const list = await screen.findByTestId('lint-validation-catalog-list');
    expect(
      within(list).getByTestId('lint-validation-catalog-entry-XML_SCHEMA'),
    ).toBeInTheDocument();
    expect(
      within(list).queryByTestId('lint-validation-catalog-entry-AMD_PRESENT'),
    ).not.toBeInTheDocument();
  });

  it('sorts by level, family, and source access (TC-EV062-006)', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    const list = await screen.findByTestId('lint-validation-catalog-list');

    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-sort'),
      'level',
    );
    let codes = within(list)
      .getAllByRole('row')
      .slice(1)
      .map((row) => row.querySelector('td')?.textContent?.trim());
    expect(codes?.[0]).toBe('XML_SCHEMA');

    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-sort'),
      'family',
    );
    codes = within(list)
      .getAllByRole('row')
      .slice(1)
      .map((row) => row.querySelector('td')?.textContent?.trim());
    expect(codes).toContain('XML_SCHEMA');
    expect(codes).toContain('AMD_PRESENT');

    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-sort'),
      'source_access',
    );
    codes = within(list)
      .getAllByRole('row')
      .slice(1)
      .map((row) => row.querySelector('td')?.textContent?.trim());
    expect(codes?.length).toBe(4);
  });

  it('renders non-clickable http when status is not verified', async () => {
    fetchLintIssueCatalog.mockResolvedValueOnce({
      issues: [
        {
          code: 'LEGACY_HTTP',
          severity: 'warning',
          message_template: 'Legacy alias landing',
          family: 'lint',
          issue_type: 'other',
          source_access: 'public',
          source_url: 'https://example.invalid/legacy',
          status: 'legacy_alias',
        },
      ],
    });
    render(<LintValidationCatalogPage />);
    const row = await screen.findByTestId('lint-validation-catalog-entry-LEGACY_HTTP');
    expect(within(row).queryByRole('link')).not.toBeInTheDocument();
    expect(row).toHaveTextContent('https://example.invalid/legacy');
    expect(row).toHaveTextContent('other');
  });

  it('shows em dash when issue_type is missing', async () => {
    fetchLintIssueCatalog.mockResolvedValueOnce({
      issues: [
        {
          code: 'NO_TYPE',
          severity: 'info',
          message_template: 'Type omitted',
          family: 'lint',
          source_url: null,
          status: 'verified',
        },
      ],
    });
    render(<LintValidationCatalogPage />);
    const row = await screen.findByTestId('lint-validation-catalog-entry-NO_TYPE');
    const cells = within(row).getAllByRole('cell');
    expect(cells[1]).toHaveTextContent('—');
  });

  it('shows empty state when level filter matches nothing', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    await screen.findByTestId('lint-validation-catalog-list');
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-level-filter'),
      'critical',
    );
    expect(await screen.findByText(/No catalog entries/i)).toBeInTheDocument();
  });

  it('sorts by code and breaks level ties by code', async () => {
    const user = userEvent.setup();
    fetchLintIssueCatalog.mockResolvedValueOnce({
      issues: [
        {
          code: 'Z_LAST',
          severity: 'error',
          message_template: 'Z',
          family: 'lint',
          issue_type: 'content',
          source_access: 'public',
          source_url: 'https://example.invalid/z',
          status: 'verified',
        },
        {
          code: 'A_FIRST',
          severity: 'error',
          message_template: 'A',
          family: 'iwxxm',
          issue_type: 'iwxxm_schema',
          source_access: 'paywall',
          source_url: 'https://example.invalid/a',
          status: 'verified',
        },
        {
          code: 'M_MID',
          severity: 'warning',
          message_template: 'M',
          family: '',
          issue_type: '',
          source_access: '',
          source_url: 'http://example.invalid/m',
          status: 'verified',
        },
      ],
    });
    render(<LintValidationCatalogPage />);
    const list = await screen.findByTestId('lint-validation-catalog-list');

    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-sort'),
      'code',
    );
    let codes = within(list)
      .getAllByRole('row')
      .slice(1)
      .map((row) => row.querySelector('td')?.textContent?.trim());
    expect(codes).toEqual(['A_FIRST', 'M_MID', 'Z_LAST']);

    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-sort'),
      'level',
    );
    codes = within(list)
      .getAllByRole('row')
      .slice(1)
      .map((row) => row.querySelector('td')?.textContent?.trim());
    // errors first (A before Z), then warning
    expect(codes).toEqual(['A_FIRST', 'Z_LAST', 'M_MID']);

    // http:// verified landing is clickable
    expect(
      within(list)
        .getByTestId('lint-validation-catalog-entry-M_MID')
        .querySelector('a'),
    ).toHaveAttribute('href', 'http://example.invalid/m');
  });

  it('ranks unknown severity last when sorting by level', async () => {
    const user = userEvent.setup();
    fetchLintIssueCatalog.mockResolvedValueOnce({
      issues: [
        {
          code: 'UNKNOWN_SEV',
          severity: 'notice',
          message_template: 'odd',
          family: 'lint',
          issue_type: 'other',
          source_access: 'public',
          source_url: 'https://example.invalid/u',
          status: 'verified',
        },
        {
          code: 'INFO_SEV',
          severity: 'info',
          message_template: 'info',
          family: 'lint',
          issue_type: 'presence',
          source_access: 'public',
          source_url: 'https://example.invalid/i',
          status: 'verified',
        },
      ],
    });
    render(<LintValidationCatalogPage />);
    const list = await screen.findByTestId('lint-validation-catalog-list');
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-sort'),
      'level',
    );
    const codes = within(list)
      .getAllByRole('row')
      .slice(1)
      .map((row) => row.querySelector('td')?.textContent?.trim());
    expect(codes).toEqual(['INFO_SEV', 'UNKNOWN_SEV']);
  });

  it('passes combined family, type, and access filters to the API', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    await screen.findByTestId('lint-validation-catalog-list');

    fetchLintIssueCatalog.mockResolvedValue({ issues: [] });
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-family-filter'),
      'lint',
    );
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-type-filter'),
      'structure',
    );
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-access-filter'),
      'paywall',
    );

    expect(fetchLintIssueCatalog).toHaveBeenCalledWith({
      family: 'lint',
      issue_type: 'structure',
      source_access: 'paywall',
    });
    expect(await screen.findByText(/No catalog entries/i)).toBeInTheDocument();
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
