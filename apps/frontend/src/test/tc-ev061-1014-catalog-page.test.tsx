/**
 * LintValidationCatalogPage unit coverage (#1014 / TC-EV061-1014).
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LintValidationCatalogPage } from '../app/components/LintValidationCatalogPage';
import { CATALOG_VIEW_STORAGE_KEY } from '../utils/catalogView';

const fetchLintIssueCatalog = vi.hoisted(() => vi.fn());
const fetchRuleCatalog = vi.hoisted(() => vi.fn());

vi.mock('@/utils/api', () => ({
  fetchLintIssueCatalog: (...args: unknown[]) => fetchLintIssueCatalog(...args),
  fetchRuleCatalog: (...args: unknown[]) => fetchRuleCatalog(...args),
}));

/**
 * Codes in the order the catalog list renders them.
 *
 * @param list - Catalog list region
 * @returns Rule codes from top to bottom
 */
function listedCodes(list: HTMLElement): string[] {
  return [
    ...list.querySelectorAll('[data-testid^="lint-validation-catalog-entry-"]'),
  ].map((row) =>
    (row.getAttribute('data-testid') ?? '').replace(
      'lint-validation-catalog-entry-',
      '',
    ),
  );
}

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
    semantic_profiles: [],
    exchange_profiles: ['GLOBAL_AFS'],
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
    semantic_profiles: ['ICAO_2025', 'CA_ECCC'],
    exchange_profiles: [],
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
    semantic_profiles: ['ICAO_2025'],
    exchange_profiles: [],
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
    semantic_profiles: [],
    exchange_profiles: [],
  },
];

describe('LintValidationCatalogPage', () => {
  beforeEach(() => {
    sessionStorage.removeItem(CATALOG_VIEW_STORAGE_KEY);
    fetchLintIssueCatalog.mockReset();
    fetchRuleCatalog.mockReset();
    fetchLintIssueCatalog.mockResolvedValue({ issues: BASE_ISSUES });
    fetchRuleCatalog.mockResolvedValue({
      family: 'conversion',
      items: [
        {
          id: 'ICAO_2025',
          title: 'ICAO_2025',
          summary: 'Semantic conversion profile ICAO_2025',
          tags: ['conversion'],
        },
      ],
    });
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

  it('loads conversion family via rule-catalogs', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    await screen.findByTestId('lint-validation-catalog-list');

    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-family-filter'),
      'conversion',
    );

    expect(fetchRuleCatalog).toHaveBeenLastCalledWith({ family: 'conversion' });
    const list = await screen.findByTestId('lint-validation-catalog-list');
    expect(
      within(list).getByTestId('lint-validation-catalog-entry-ICAO_2025'),
    ).toBeInTheDocument();
  });

  it('maps rule-catalog rows with missing severity/summary fallbacks', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    await screen.findByTestId('lint-validation-catalog-list');

    fetchRuleCatalog.mockResolvedValueOnce({
      family: 'conversion',
      items: [
        { id: 'BARE', title: 'Bare title', summary: '' },
        {
          id: 'TAGGED',
          title: 'Tagged',
          summary: 'Has summary',
          severity: 'warning',
          tags: ['x'],
        },
      ],
    });
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-family-filter'),
      'conversion',
    );
    const bare = await screen.findByTestId('lint-validation-catalog-entry-BARE');
    expect(bare).toHaveTextContent('Bare title');
    // Missing severity/type/access are not invented as info/other/public.
    expect(within(bare).getByTestId('catalog-entry-type')).toHaveTextContent('—');
    expect(within(bare).getByTestId('catalog-entry-level')).toHaveTextContent('—');
    expect(bare).not.toHaveTextContent('Access: public');
    expect(
      await screen.findByTestId('lint-validation-catalog-entry-TAGGED'),
    ).toHaveTextContent('Has summary');
  });

  it('treats missing rule-catalog items as empty', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    await screen.findByTestId('lint-validation-catalog-list');

    fetchRuleCatalog.mockResolvedValueOnce({ family: 'decoding', items: undefined });
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-family-filter'),
      'decoding',
    );
    expect(await screen.findByText(/No catalog entries/i)).toBeInTheDocument();
  });

  it('loads dissemination family via rule-catalogs', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    await screen.findByTestId('lint-validation-catalog-list');

    fetchRuleCatalog.mockResolvedValueOnce({
      family: 'dissemination',
      items: [{ id: 'GLOBAL_AFS', title: 'GLOBAL_AFS', summary: 'exchange' }],
    });
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-family-filter'),
      'dissemination',
    );
    expect(fetchRuleCatalog).toHaveBeenLastCalledWith({ family: 'dissemination' });
    expect(
      await screen.findByTestId('lint-validation-catalog-entry-GLOBAL_AFS'),
    ).toBeInTheDocument();
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

    const codes = listedCodes(list);
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

  it('shows the rule text without semantic or exchange profile lines', async () => {
    render(<LintValidationCatalogPage />);
    const xmlSchema = await screen.findByTestId(
      'lint-validation-catalog-entry-XML_SCHEMA',
    );
    expect(xmlSchema).toHaveTextContent(
      'IWXXM document must validate against the pinned XSD schema',
    );
    expect(xmlSchema).not.toHaveTextContent(/semantic profile/i);
    expect(xmlSchema).not.toHaveTextContent(/exchange profile/i);
    expect(xmlSchema).not.toHaveTextContent(/^Profiles:/m);
    expect(
      screen.queryByTestId('lint-validation-catalog-profile-filter'),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId('lint-validation-catalog-exchange-filter'),
    ).not.toBeInTheDocument();
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
    let codes = listedCodes(list);
    expect(codes[0]).toBe('XML_SCHEMA');

    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-sort'),
      'family',
    );
    codes = listedCodes(list);
    expect(codes).toContain('XML_SCHEMA');
    expect(codes).toContain('AMD_PRESENT');

    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-sort'),
      'source_access',
    );
    codes = listedCodes(list);
    expect(codes.length).toBe(4);
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
    expect(within(row).getByTestId('catalog-entry-type')).toHaveTextContent('—');
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
    let codes = listedCodes(list);
    expect(codes).toEqual(['A_FIRST', 'M_MID', 'Z_LAST']);

    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-sort'),
      'level',
    );
    codes = listedCodes(list);
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
    const codes = listedCodes(list);
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
    const user = userEvent.setup();
    fetchLintIssueCatalog.mockResolvedValueOnce({ issues: [] });
    const { unmount } = render(<LintValidationCatalogPage />);
    expect(await screen.findByText(/No catalog entries/i)).toBeInTheDocument();
    unmount();

    fetchLintIssueCatalog.mockRejectedValueOnce(new Error('Failed to fetch'));
    const { unmount: unmount2 } = render(<LintValidationCatalogPage />);
    expect(await screen.findByRole('alert')).toHaveTextContent(
      'The catalog could not be loaded.',
    );
    expect(screen.getByRole('alert')).not.toHaveTextContent('Failed to fetch');
    expect(screen.getByTestId('lint-validation-catalog-retry')).toBeInTheDocument();
    unmount2();

    fetchLintIssueCatalog.mockRejectedValueOnce('offline');
    fetchLintIssueCatalog.mockResolvedValueOnce({
      issues: [
        {
          code: 'RETRIED',
          severity: 'info',
          message_template: 'Loaded after retry',
          family: 'lint',
          status: 'verified',
        },
      ],
    });
    render(<LintValidationCatalogPage />);
    expect(await screen.findByRole('alert')).toHaveTextContent(
      'The catalog could not be loaded.',
    );
    await user.click(screen.getByTestId('lint-validation-catalog-retry'));
    expect(
      await screen.findByTestId('lint-validation-catalog-entry-RETRIED'),
    ).toBeInTheDocument();
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

  it('keeps catalog copy free of planning ids', async () => {
    render(<LintValidationCatalogPage />);
    await screen.findByTestId('lint-validation-catalog-list');
    expect(screen.queryByText(/EV-1120|TC-EV|#1123|ADR-/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/All semantic profiles/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/All exchange profiles/i)).not.toBeInTheDocument();
  });

  const RULE_FAMILIES = ['conversion', 'dissemination', 'decoding'] as const;

  for (const family of RULE_FAMILIES) {
    it(`TC-EV1281: ${family} Type/Level/Access/Sort are client-only (#1281)`, async () => {
      const user = userEvent.setup();
      render(<LintValidationCatalogPage />);
      await screen.findByTestId('lint-validation-catalog-list');

      fetchRuleCatalog.mockResolvedValue({
        family,
        items: [
          { id: 'ZULU', title: 'Zulu', summary: 'z row', severity: 'warning' },
          { id: 'ALPHA', title: 'Alpha', summary: 'a row', severity: 'error' },
          { id: 'MIKE', title: 'Mike', summary: 'm row' },
        ],
      });
      await user.selectOptions(
        screen.getByTestId('lint-validation-catalog-family-filter'),
        family,
      );
      const list = await screen.findByTestId('lint-validation-catalog-list');
      expect(fetchRuleCatalog).toHaveBeenLastCalledWith({ family });

      // Unsorted fixtures → Sort by Code reorders by id.
      await user.selectOptions(
        screen.getByTestId('lint-validation-catalog-sort'),
        'code',
      );
      let codes = listedCodes(list);
      expect(codes).toEqual(['ALPHA', 'MIKE', 'ZULU']);

      // Sort by Level uses real severity; missing severity is last (not invented info).
      await user.selectOptions(
        screen.getByTestId('lint-validation-catalog-sort'),
        'level',
      );
      codes = listedCodes(list);
      expect(codes).toEqual(['ALPHA', 'ZULU', 'MIKE']);

      // Type value no row has → empty; All restores.
      // Conversion uses profile|policy|other; dissemination uses profile|other.
      // Decoding keeps the TAC/IWXXM type list (e.g. structure).
      const emptyType =
        family === 'conversion'
          ? 'policy'
          : family === 'dissemination'
            ? 'profile'
            : 'structure';
      await user.selectOptions(
        screen.getByTestId('lint-validation-catalog-type-filter'),
        emptyType,
      );
      expect(await screen.findByText(/No catalog entries/i)).toBeInTheDocument();
      expect(fetchRuleCatalog).toHaveBeenLastCalledWith({ family });
      await user.selectOptions(
        screen.getByTestId('lint-validation-catalog-type-filter'),
        'all',
      );
      expect(
        await screen.findByTestId('lint-validation-catalog-entry-ALPHA'),
      ).toBeInTheDocument();

      // Access value no row has → empty; All restores. Missing access ≠ public.
      await user.selectOptions(
        screen.getByTestId('lint-validation-catalog-access-filter'),
        'public',
      );
      expect(await screen.findByText(/No catalog entries/i)).toBeInTheDocument();
      await user.selectOptions(
        screen.getByTestId('lint-validation-catalog-access-filter'),
        'all',
      );
      expect(
        await screen.findByTestId('lint-validation-catalog-entry-ZULU'),
      ).toBeInTheDocument();

      // Level=info must not match rows with missing severity.
      await user.selectOptions(
        screen.getByTestId('lint-validation-catalog-level-filter'),
        'info',
      );
      expect(await screen.findByText(/No catalog entries/i)).toBeInTheDocument();
      await user.selectOptions(
        screen.getByTestId('lint-validation-catalog-level-filter'),
        'error',
      );
      expect(
        await screen.findByTestId('lint-validation-catalog-entry-ALPHA'),
      ).toBeInTheDocument();
      expect(
        screen.queryByTestId('lint-validation-catalog-entry-ZULU'),
      ).not.toBeInTheDocument();
      expect(
        screen.queryByTestId('lint-validation-catalog-entry-MIKE'),
      ).not.toBeInTheDocument();

      // Never add type/level/access/sort query params for rule catalogs.
      for (const call of fetchRuleCatalog.mock.calls) {
        expect(call[0]).toEqual({ family: expect.any(String) });
        expect(call[0]).not.toHaveProperty('issue_type');
        expect(call[0]).not.toHaveProperty('source_access');
        expect(call[0]).not.toHaveProperty('sort');
      }
      expect(fetchLintIssueCatalog).not.toHaveBeenCalledWith(
        expect.objectContaining({ family }),
      );
    });
  }

  it('searches the catalog and opens the selected rule', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    const detail = await screen.findByTestId('lint-validation-catalog-detail');
    expect(detail).toHaveTextContent('AMD_PRESENT');

    await user.click(
      within(screen.getByTestId('lint-validation-catalog-entry-XML_SCHEMA')).getByRole(
        'button',
      ),
    );
    expect(screen.getByTestId('lint-validation-catalog-detail')).toHaveTextContent(
      'XML_SCHEMA',
    );
    expect(screen.getByTestId('lint-validation-catalog-detail')).toHaveTextContent(
      'IWXXM validation',
    );

    await user.type(screen.getByTestId('lint-validation-catalog-search'), 'vendor pin');
    expect(
      screen.getByTestId('lint-validation-catalog-entry-VENDOR_ONLY'),
    ).toBeInTheDocument();
    expect(
      screen.queryByTestId('lint-validation-catalog-entry-XML_SCHEMA'),
    ).not.toBeInTheDocument();
    expect(screen.getByTestId('lint-validation-catalog-detail')).toHaveTextContent(
      'VENDOR_ONLY',
    );
  });

  it('shows packaged pass and fail reports and says when an example is not on file', async () => {
    const user = userEvent.setup();
    fetchLintIssueCatalog.mockResolvedValue({
      issues: [
        ...BASE_ISSUES,
        {
          code: 'MISSING_CCCC',
          severity: 'error',
          message_template: 'Station identifier is missing',
          product: 'metar',
          tags: ['station'],
          family: 'lint',
          issue_type: 'presence',
          source_access: 'paywall',
          status: 'verified',
          semantic_profiles: [],
          exchange_profiles: [],
        },
        {
          code: 'MISSING_DTG',
          severity: 'error',
          message_template: 'Advisory time is missing',
          product: 'vaa',
          tags: ['time'],
          family: 'lint',
          issue_type: 'presence',
          source_access: 'public',
          status: 'verified',
          semantic_profiles: [],
          exchange_profiles: [],
        },
        {
          code: 'AT_PRESENT',
          severity: 'info',
          message_template: 'AT change group noted',
          product: 'taf',
          tags: ['change'],
          family: 'lint',
          issue_type: 'presence',
          source_access: 'public',
          status: 'verified',
          semantic_profiles: [],
          exchange_profiles: [],
        },
        {
          code: 'INFO_NO_SAMPLE',
          severity: 'info',
          message_template: 'Info rule with no packaged report',
          product: 'taf',
          tags: ['time'],
          family: 'lint',
          issue_type: 'presence',
          source_access: 'public',
          status: 'verified',
          semantic_profiles: [],
          exchange_profiles: [],
        },
      ],
    });
    render(<LintValidationCatalogPage />);
    const infoDetail = await screen.findByTestId('lint-validation-catalog-detail');
    const infoExample = within(infoDetail).getByTestId('catalog-rule-example');
    expect(infoExample).toHaveAttribute('data-tone', 'example');
    expect(infoExample).toHaveTextContent('TAF KJFK');
    expect(infoExample).not.toHaveTextContent('YUDO');
    expect(
      within(infoDetail).getByRole('heading', { name: /^Examples$/ }),
    ).toBeInTheDocument();
    expect(
      within(infoDetail).queryByRole('heading', { name: 'Passing example' }),
    ).not.toBeInTheDocument();
    expect(
      within(infoDetail).queryByRole('heading', { name: 'Failing example' }),
    ).not.toBeInTheDocument();
    expect(
      within(infoDetail).queryByText(/passing|failing|succeeding/i),
    ).not.toBeInTheDocument();
    expect(
      within(infoDetail).queryByTestId('catalog-rule-example-fail'),
    ).not.toBeInTheDocument();
    expect(
      within(infoDetail).queryByTestId('catalog-rule-example-pass'),
    ).not.toBeInTheDocument();

    await user.click(
      within(
        screen.getByTestId('lint-validation-catalog-entry-MISSING_CCCC'),
      ).getByRole('button'),
    );
    expect(screen.getByTestId('catalog-rule-example-pass')).toHaveAttribute(
      'data-tone',
      'pass',
    );
    expect(screen.getByTestId('catalog-rule-example-pass')).toHaveTextContent('KJFK');
    expect(screen.getByTestId('catalog-rule-example-fail')).toHaveAttribute(
      'data-tone',
      'fail',
    );
    expect(screen.getByTestId('catalog-rule-example-fail')).not.toHaveTextContent(
      'KJFK',
    );

    await user.click(
      within(screen.getByTestId('lint-validation-catalog-entry-MISSING_DTG')).getByRole(
        'button',
      ),
    );
    expect(screen.getByTestId('catalog-rule-example-pass')).toHaveAttribute(
      'data-tone',
      'pass',
    );
    expect(screen.getByTestId('catalog-rule-example-pass')).toHaveTextContent('DTG:');
    expect(screen.getByTestId('catalog-rule-example-fail')).toHaveAttribute(
      'data-tone',
      'fail',
    );
    expect(screen.getByTestId('catalog-rule-example-fail')).toHaveTextContent(
      'VA ADVISORY',
    );

    await user.click(
      within(screen.getByTestId('lint-validation-catalog-entry-AT_PRESENT')).getByRole(
        'button',
      ),
    );
    const atPresent = screen.getByTestId('lint-validation-catalog-detail');
    expect(within(atPresent).getByTestId('catalog-rule-example')).toHaveTextContent(
      'TAF KJFK',
    );
    expect(within(atPresent).getByTestId('catalog-rule-example')).not.toHaveTextContent(
      'BECMG',
    );
    expect(
      within(atPresent).getByRole('heading', { name: /^Examples$/ }),
    ).toBeInTheDocument();
    expect(
      within(atPresent).queryByRole('heading', { name: 'Failing example' }),
    ).not.toBeInTheDocument();

    await user.click(
      within(
        screen.getByTestId('lint-validation-catalog-entry-INFO_NO_SAMPLE'),
      ).getByRole('button'),
    );
    const emptyInfo = screen.getByTestId('lint-validation-catalog-detail');
    expect(within(emptyInfo).getByTestId('catalog-rule-example')).toHaveAttribute(
      'data-tone',
      'unavailable',
    );
    expect(within(emptyInfo).getByTestId('catalog-rule-example')).toHaveTextContent(
      'No example is available for this rule yet.',
    );
    expect(
      within(emptyInfo).queryByText(/passing|failing|succeeding/i),
    ).not.toBeInTheDocument();

    await user.click(
      within(screen.getByTestId('lint-validation-catalog-entry-VENDOR_ONLY')).getByRole(
        'button',
      ),
    );
    const warningDetail = screen.getByTestId('lint-validation-catalog-detail');
    expect(
      within(warningDetail).getByRole('heading', { name: /^Passing example$/ }),
    ).toBeInTheDocument();
    expect(
      within(warningDetail).getByRole('heading', { name: /^Failing example$/ }),
    ).toBeInTheDocument();
    expect(
      within(warningDetail).getByTestId('catalog-rule-example-pass'),
    ).toHaveAttribute('data-tone', 'unavailable');
    expect(
      within(warningDetail).getByTestId('catalog-rule-example-fail'),
    ).toHaveAttribute('data-tone', 'unavailable');
  });

  it('switches between compact and detailed and keeps search and the selected rule', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    expect(
      await screen.findByTestId('lint-validation-catalog-view-detailed'),
    ).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByTestId('catalog-detail-facts')).toBeInTheDocument();
    expect(
      within(
        screen.getByTestId('lint-validation-catalog-entry-AMD_PRESENT'),
      ).getByTestId('catalog-entry-type'),
    ).toBeInTheDocument();

    await user.click(screen.getByTestId('lint-validation-catalog-view-compact'));
    expect(screen.getByTestId('lint-validation-catalog-view-compact')).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    expect(document.querySelector('[data-view="compact"]')).toBeTruthy();
    expect(
      within(
        screen.getByTestId('lint-validation-catalog-entry-AMD_PRESENT'),
      ).queryByTestId('catalog-entry-type'),
    ).not.toBeInTheDocument();
    expect(screen.queryByTestId('catalog-detail-facts')).not.toBeInTheDocument();
    expect(screen.getByTestId('lint-validation-catalog-detail')).toHaveTextContent(
      'AMD_PRESENT',
    );

    await user.type(screen.getByTestId('lint-validation-catalog-search'), 'vendor pin');
    expect(
      screen.getByTestId('lint-validation-catalog-entry-VENDOR_ONLY'),
    ).toBeInTheDocument();
    expect(
      screen.queryByTestId('lint-validation-catalog-entry-AMD_PRESENT'),
    ).not.toBeInTheDocument();
    expect(screen.getByTestId('lint-validation-catalog-detail')).toHaveTextContent(
      'VENDOR_ONLY',
    );

    await user.click(screen.getByTestId('lint-validation-catalog-view-detailed'));
    expect(screen.getByTestId('catalog-detail-facts')).toHaveTextContent('structure');
    expect(sessionStorage.getItem(CATALOG_VIEW_STORAGE_KEY)).toBe('detailed');

    cleanup();
    sessionStorage.setItem(CATALOG_VIEW_STORAGE_KEY, 'compact');
    render(<LintValidationCatalogPage />);
    expect(
      await screen.findByTestId('lint-validation-catalog-view-compact'),
    ).toHaveAttribute('aria-pressed', 'true');
  });
});
