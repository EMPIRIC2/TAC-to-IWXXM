/**
 * TC-EV1308-003 — Family-aware catalog type filter + rule-catalog pass-through.
 *
 * [Corpus: journeys UJ-080] [Corpus: tests] #1308
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  CONVERSION_TYPE_OPTIONS,
  DISSEMINATION_TYPE_OPTIONS,
  EV062_TYPE_OPTIONS,
  LintValidationCatalogPage,
  ALL_FAMILY_TYPE_OPTIONS,
  mapRuleCatalogItem,
  typeOptionsForFamily,
} from '../app/components/LintValidationCatalogPage';

const fetchLintIssueCatalog = vi.hoisted(() => vi.fn());
const fetchRuleCatalog = vi.hoisted(() => vi.fn());

vi.mock('@/utils/api', () => ({
  fetchLintIssueCatalog: (...args: unknown[]) => fetchLintIssueCatalog(...args),
  fetchRuleCatalog: (...args: unknown[]) => fetchRuleCatalog(...args),
}));

describe('TC-EV1308-003 family-aware type filter', () => {
  beforeEach(() => {
    fetchLintIssueCatalog.mockReset();
    fetchRuleCatalog.mockReset();
    fetchLintIssueCatalog.mockResolvedValue({ issues: [] });
    fetchRuleCatalog.mockResolvedValue({ family: 'decoding', items: [] });
  });

  it('typeOptionsForFamily returns EV-062 for decoding and conversion set for conversion', () => {
    expect(typeOptionsForFamily('decoding')).toEqual([...EV062_TYPE_OPTIONS]);
    expect(typeOptionsForFamily('conversion')).toEqual([...CONVERSION_TYPE_OPTIONS]);
    expect(typeOptionsForFamily('dissemination')).toEqual([
      ...DISSEMINATION_TYPE_OPTIONS,
    ]);
    expect(typeOptionsForFamily('lint')).toEqual([...EV062_TYPE_OPTIONS]);
    expect(typeOptionsForFamily('iwxxm')).toEqual([...EV062_TYPE_OPTIONS]);
    expect(typeOptionsForFamily('all')).toEqual([...ALL_FAMILY_TYPE_OPTIONS]);
  });

  it('mapRuleCatalogItem passes additive fields and does not invent defaults', () => {
    const mapped = mapRuleCatalogItem(
      {
        id: 'TS',
        title: 'TS',
        summary: 'thunderstorm',
        severity: 'info',
        tags: ['decoding'],
        issue_type: 'content',
        source_url: 'https://example.invalid/codes',
        source_attribution: 'WMO code list',
        source_access: 'public',
        source_locator: 'weather phenomena',
        conform_note: 'TAC hazard abbreviation',
      },
      'decoding',
    );
    expect(mapped.issue_type).toBe('content');
    expect(mapped.severity).toBe('info');
    expect(mapped.source_url).toBe('https://example.invalid/codes');
    expect(mapped.source_attribution).toBe('WMO code list');
    expect(mapped.source_access).toBe('public');
    expect(mapped.source_locator).toBe('weather phenomena');
    expect(mapped.message_template).toContain('thunderstorm');
    expect(mapped.message_template).toContain('TAC hazard abbreviation');
    expect(mapped.status).toBeNull();

    const bare = mapRuleCatalogItem({ id: 'X', title: 'X' }, 'conversion');
    expect(bare.issue_type).toBeNull();
    expect(bare.severity).toBe('');
    expect(bare.source_url).toBeNull();
    expect(bare.source_access).toBeNull();
    expect(bare.source_locator).toBeNull();
  });

  it('Conversion type filter shows profile/policy/other; null type displays as em dash', async () => {
    const user = userEvent.setup();
    fetchRuleCatalog.mockResolvedValue({
      family: 'conversion',
      items: [
        {
          id: 'icao_2025',
          title: 'icao_2025',
          summary: 'Annex 3 conversion profile for standard IWXXM encoding.',
          issue_type: 'profile',
          severity: null,
          tags: ['conversion', 'profile'],
        },
        {
          id: 'sparse',
          title: 'sparse',
          summary: 'Row without type',
          tags: ['conversion'],
        },
      ],
    });

    render(<LintValidationCatalogPage />);
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-family-filter'),
      'conversion',
    );
    await screen.findByTestId('lint-validation-catalog-entry-icao_2025');

    const typeFilter = screen.getByTestId('lint-validation-catalog-type-filter');
    const optionValues = within(typeFilter)
      .getAllByRole('option')
      .map((opt) => (opt as HTMLOptionElement).value);
    expect(optionValues).toEqual(['all', 'profile', 'policy', 'other']);
    expect(optionValues).not.toContain('structure');
    expect(optionValues).not.toContain('presence');

    const sparseRow = screen.getByTestId('lint-validation-catalog-entry-sparse');
    expect(within(sparseRow).getByTestId('catalog-entry-type').textContent).toBe(
      'Type: —',
    );

    await user.selectOptions(typeFilter, 'profile');
    expect(
      screen.getByTestId('lint-validation-catalog-entry-icao_2025'),
    ).toBeInTheDocument();
    expect(
      screen.queryByTestId('lint-validation-catalog-entry-sparse'),
    ).not.toBeInTheDocument();
  });

  it('Decoding type filter keeps EV-062 options', async () => {
    const user = userEvent.setup();
    fetchRuleCatalog.mockResolvedValue({
      family: 'decoding',
      items: [
        {
          id: 'TS',
          title: 'TS',
          summary: 'thunderstorm',
          issue_type: 'content',
          tags: ['decoding'],
        },
      ],
    });

    render(<LintValidationCatalogPage />);
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-family-filter'),
      'decoding',
    );
    await screen.findByTestId('lint-validation-catalog-entry-TS');

    const optionValues = within(
      screen.getByTestId('lint-validation-catalog-type-filter'),
    )
      .getAllByRole('option')
      .map((opt) => (opt as HTMLOptionElement).value);
    expect(optionValues).toEqual([...EV062_TYPE_OPTIONS]);
  });

  it('switching family resets incompatible type filter to All', async () => {
    const user = userEvent.setup();
    fetchRuleCatalog.mockImplementation(async ({ family }: { family: string }) => ({
      family,
      items:
        family === 'conversion'
          ? [
              {
                id: 'icao_2025',
                title: 'icao_2025',
                summary: 'Annex 3 profile',
                issue_type: 'profile',
              },
            ]
          : [
              {
                id: 'TS',
                title: 'TS',
                summary: 'thunderstorm',
                issue_type: 'content',
              },
            ],
    }));

    render(<LintValidationCatalogPage />);
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-family-filter'),
      'conversion',
    );
    await screen.findByTestId('lint-validation-catalog-entry-icao_2025');
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-type-filter'),
      'profile',
    );

    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-family-filter'),
      'decoding',
    );
    await screen.findByTestId('lint-validation-catalog-entry-TS');
    expect(screen.getByTestId('lint-validation-catalog-type-filter')).toHaveValue(
      'all',
    );
  });
});
