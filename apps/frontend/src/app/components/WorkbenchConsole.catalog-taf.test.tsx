/**
 * T5.1 / TC-F20-005 — catalog panel filters/copy for TAF tags (E15-14).
 *
 * Green after T5.2: list rows show tags (+ product when set); tag filter
 * narrows to `taf`.
 */

import { describe, expect, it, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { WorkbenchConsole } from './WorkbenchConsole';
import type { LintIssueCatalogEntry } from '@/utils/api';

vi.mock('/utils/convertParams', () => ({
  consoleLevelPasses: () => true,
}));

const TAF_ONLY: LintIssueCatalogEntry = {
  code: 'FM_PRESENT',
  severity: 'info',
  message_template: '{product} FM change group present — research T2',
  product: 'taf',
  tags: ['change', 'taf', 't2', 'fm'],
};

const SHARED: LintIssueCatalogEntry = {
  code: 'CAVOK_PRESENT',
  severity: 'info',
  message_template: '{product} CAVOK present — research T3 / S1',
  product: null,
  tags: ['cavok', 'metar', 'speci', 'taf', 't3', 's1'],
};

const METAR_ONLY: LintIssueCatalogEntry = {
  code: 'MISSING_TERMINATOR',
  severity: 'info',
  message_template: "Reports in bulletins end with '='",
  product: null,
  tags: ['terminator', 'metar', 'speci'],
};

const ENTRIES = [TAF_ONLY, SHARED, METAR_ONLY];

async function openCatalog(user: ReturnType<typeof userEvent.setup>) {
  render(<WorkbenchConsole defaultOpen lines={[]} catalogEntries={ENTRIES} />);
  await user.click(screen.getByTestId('lint-issue-catalog-toggle'));
  return screen.getByTestId('lint-issue-catalog-list');
}

describe('WorkbenchConsole catalog TAF tags (T5.1 / E15-14)', () => {
  it('shows tags (and product when set) in catalog list copy', async () => {
    const user = userEvent.setup();
    const list = await openCatalog(user);

    const fm = within(list).getByTestId('lint-issue-catalog-entry-FM_PRESENT');
    expect(fm).toHaveTextContent('FM_PRESENT');
    expect(fm).toHaveTextContent('taf');
    expect(fm).toHaveTextContent(/change/);
    expect(fm).toHaveTextContent(/product:\s*taf/i);

    const cavok = within(list).getByTestId('lint-issue-catalog-entry-CAVOK_PRESENT');
    expect(cavok).toHaveTextContent(/taf/);
    expect(cavok).not.toHaveTextContent(/product:/i);
  });

  it('filters the catalog list to taf-tagged rows via tag filter', async () => {
    const user = userEvent.setup();
    await openCatalog(user);

    const filter = screen.getByTestId('lint-issue-catalog-tag-filter');
    await user.selectOptions(filter, 'taf');

    const list = screen.getByTestId('lint-issue-catalog-list');
    expect(
      within(list).getByTestId('lint-issue-catalog-entry-FM_PRESENT'),
    ).toBeInTheDocument();
    expect(
      within(list).getByTestId('lint-issue-catalog-entry-CAVOK_PRESENT'),
    ).toBeInTheDocument();
    expect(
      within(list).queryByTestId('lint-issue-catalog-entry-MISSING_TERMINATOR'),
    ).not.toBeInTheDocument();

    expect(screen.getByTestId('lint-issue-catalog-toggle')).toHaveTextContent(/2/);
  });

  it('restores all rows when tag filter is cleared to all', async () => {
    const user = userEvent.setup();
    await openCatalog(user);

    const filter = screen.getByTestId('lint-issue-catalog-tag-filter');
    await user.selectOptions(filter, 'taf');
    await user.selectOptions(filter, '');

    const list = screen.getByTestId('lint-issue-catalog-list');
    expect(
      within(list).getByTestId('lint-issue-catalog-entry-MISSING_TERMINATOR'),
    ).toBeInTheDocument();
    expect(screen.getByTestId('lint-issue-catalog-toggle')).toHaveTextContent(/3/);
  });
});
