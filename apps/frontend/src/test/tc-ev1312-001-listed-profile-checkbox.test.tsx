/**
 * TC-EV1312-001 — Optional Only rules that list this profile checkbox.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  entryMatchesListedProfileFilter,
  LintValidationCatalogPage,
} from '../app/components/LintValidationCatalogPage';
import type { LintIssueCatalogEntry } from '@/utils/openapiTypes';
import {
  LINT_VALIDATION_CATALOG_LISTED_PROFILE_NEEDS_PROFILE,
  LINT_VALIDATION_CATALOG_LISTED_PROFILE_ONLY,
} from '@/utils/lintValidationCatalogCopy';

const fetchLintIssueCatalog = vi.hoisted(() => vi.fn());
const fetchRuleCatalog = vi.hoisted(() => vi.fn());

vi.mock('@/utils/api', () => ({
  fetchLintIssueCatalog: (...args: unknown[]) => fetchLintIssueCatalog(...args),
  fetchRuleCatalog: (...args: unknown[]) => fetchRuleCatalog(...args),
}));

const ISSUES = [
  {
    code: 'SHARED_SEMANTIC',
    severity: 'info',
    message_template: 'Shared semantic row',
    product: null,
    tags: ['terminator'],
    family: 'lint',
    issue_type: 'structure',
    source_access: 'public',
    source_url: 'https://example.com/shared',
    status: 'verified',
    semantic_profiles: [],
    exchange_profiles: ['GLOBAL_AFS'],
  },
  {
    code: 'LISTED_SEMANTIC',
    severity: 'info',
    message_template: 'Listed semantic row',
    product: null,
    tags: ['modifier'],
    family: 'lint',
    issue_type: 'presence',
    source_access: 'public',
    source_url: 'https://example.com/listed',
    status: 'verified',
    semantic_profiles: ['US_FAA_NWS'],
    exchange_profiles: [],
  },
  {
    code: 'LISTED_EXCHANGE',
    severity: 'warning',
    message_template: 'Listed exchange row',
    product: null,
    tags: ['ahl'],
    family: 'lint',
    issue_type: 'structure',
    source_access: 'public',
    source_url: 'https://example.com/ex',
    status: 'verified',
    semantic_profiles: ['ICAO_2025'],
    exchange_profiles: ['EUR_RODEX'],
  },
];

describe('entryMatchesListedProfileFilter', () => {
  const shared = ISSUES[0] as LintIssueCatalogEntry;
  const listed = ISSUES[1] as LintIssueCatalogEntry;

  it('passes all rows when listed-only is off', () => {
    expect(
      entryMatchesListedProfileFilter(shared, {
        listedOnly: false,
        semanticSelected: true,
        exchangeSelected: false,
      }),
    ).toBe(true);
  });

  it('passes all rows when no profile axis is selected', () => {
    expect(
      entryMatchesListedProfileFilter(shared, {
        listedOnly: true,
        semanticSelected: false,
        exchangeSelected: false,
      }),
    ).toBe(true);
  });

  it('excludes empty semantic_profiles when semantic axis selected', () => {
    expect(
      entryMatchesListedProfileFilter(shared, {
        listedOnly: true,
        semanticSelected: true,
        exchangeSelected: false,
      }),
    ).toBe(false);
    expect(
      entryMatchesListedProfileFilter(listed, {
        listedOnly: true,
        semanticSelected: true,
        exchangeSelected: false,
      }),
    ).toBe(true);
  });

  it('excludes empty exchange_profiles when exchange axis selected', () => {
    expect(
      entryMatchesListedProfileFilter(listed, {
        listedOnly: true,
        semanticSelected: false,
        exchangeSelected: true,
      }),
    ).toBe(false);
    expect(
      entryMatchesListedProfileFilter(ISSUES[0] as LintIssueCatalogEntry, {
        listedOnly: true,
        semanticSelected: false,
        exchangeSelected: true,
      }),
    ).toBe(true);
  });
});

describe('TC-EV1312-001 listed-profile-only checkbox', () => {
  beforeEach(() => {
    fetchLintIssueCatalog.mockReset();
    fetchRuleCatalog.mockReset();
    fetchLintIssueCatalog.mockResolvedValue({ issues: ISSUES });
    fetchRuleCatalog.mockResolvedValue({ family: 'conversion', items: [] });
  });

  it('shows checkbox with plain-language label', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    const box = await screen.findByTestId(
      'lint-validation-catalog-listed-profile-only',
    );
    expect(box).toBeDisabled();
    expect(box).toHaveAttribute(
      'aria-label',
      LINT_VALIDATION_CATALOG_LISTED_PROFILE_NEEDS_PROFILE,
    );
    expect(
      screen.getByText(LINT_VALIDATION_CATALOG_LISTED_PROFILE_NEEDS_PROFILE),
    ).toBeInTheDocument();

    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-profile-filter'),
      'US_FAA_NWS',
    );
    expect(box).toBeEnabled();
    expect(box).toHaveAttribute(
      'aria-label',
      LINT_VALIDATION_CATALOG_LISTED_PROFILE_ONLY,
    );
    expect(
      screen.getByText(LINT_VALIDATION_CATALOG_LISTED_PROFILE_ONLY),
    ).toBeInTheDocument();
  });

  it('off + profile selected keeps shared and listed rows', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    await screen.findByTestId('lint-validation-catalog-list');
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-profile-filter'),
      'US_FAA_NWS',
    );
    const list = screen.getByTestId('lint-validation-catalog-list');
    expect(
      within(list).getByTestId('lint-validation-catalog-entry-SHARED_SEMANTIC'),
    ).toBeInTheDocument();
    expect(
      within(list).getByTestId('lint-validation-catalog-entry-LISTED_SEMANTIC'),
    ).toBeInTheDocument();
  });

  it('on + profile selected hides unrestricted semantic rows', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    await screen.findByTestId('lint-validation-catalog-list');
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-profile-filter'),
      'US_FAA_NWS',
    );
    await user.click(screen.getByTestId('lint-validation-catalog-listed-profile-only'));
    const list = screen.getByTestId('lint-validation-catalog-list');
    expect(
      within(list).queryByTestId('lint-validation-catalog-entry-SHARED_SEMANTIC'),
    ).not.toBeInTheDocument();
    expect(
      within(list).getByTestId('lint-validation-catalog-entry-LISTED_SEMANTIC'),
    ).toBeInTheDocument();
  });

  it('on with both axes All does not hide unrestricted rows', async () => {
    render(<LintValidationCatalogPage />);
    await screen.findByTestId('lint-validation-catalog-list');
    const box = screen.getByTestId('lint-validation-catalog-listed-profile-only');
    expect(box).toBeDisabled();
    expect(box).not.toBeChecked();
    const list = screen.getByTestId('lint-validation-catalog-list');
    expect(
      within(list).getByTestId('lint-validation-catalog-entry-SHARED_SEMANTIC'),
    ).toBeInTheDocument();
  });

  it('clears the checkbox when Profile returns to All profiles', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    await screen.findByTestId('lint-validation-catalog-list');
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-profile-filter'),
      'US_FAA_NWS',
    );
    const box = screen.getByTestId('lint-validation-catalog-listed-profile-only');
    await user.click(box);
    expect(box).toBeChecked();
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-profile-filter'),
      'all',
    );
    expect(box).not.toBeChecked();
    expect(box).toBeDisabled();
  });

  it('clears the checkbox when Exchange returns to All exchange profiles', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    await screen.findByTestId('lint-validation-catalog-list');
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-exchange-filter'),
      'EUR_RODEX',
    );
    const box = screen.getByTestId('lint-validation-catalog-listed-profile-only');
    await user.click(box);
    expect(box).toBeChecked();
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-exchange-filter'),
      'all',
    );
    expect(box).not.toBeChecked();
    expect(box).toBeDisabled();
  });

  it('disabled for rule-catalog families', async () => {
    const user = userEvent.setup();
    render(<LintValidationCatalogPage />);
    await screen.findByTestId('lint-validation-catalog-list');
    await user.selectOptions(
      screen.getByTestId('lint-validation-catalog-family-filter'),
      'conversion',
    );
    expect(
      screen.getByTestId('lint-validation-catalog-listed-profile-only'),
    ).toBeDisabled();
  });
});
