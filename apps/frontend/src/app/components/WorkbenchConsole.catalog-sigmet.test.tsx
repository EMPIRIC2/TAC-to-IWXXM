/**
 * T5.1 / TC-F23-005 — catalog panel filters/copy for SIGMET (+ VA) tags (E19-17).
 *
 * Asserts additive reuse of F20 tag filter + list copy for `sigmet` / `va`.
 */

import { describe, expect, it, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { WorkbenchConsole } from './WorkbenchConsole';
import type { LintIssueCatalogEntry } from '@/utils/api';

vi.mock('/utils/convertParams', () => ({
  consoleLevelPasses: () => true,
}));

const SIGMET_ONLY: LintIssueCatalogEntry = {
  code: 'SIGMET_CNL',
  severity: 'info',
  message_template: 'SIGMET CNL cancel report — research G1 / C1',
  product: 'sigmet',
  tags: ['cnl', 'sigmet', 'g1', 'c1'],
};

const VA_TAGGED: LintIssueCatalogEntry = {
  code: 'NO_VA_EXP',
  severity: 'info',
  message_template: 'VA SIGMET NO VA EXP absence token — research V1 / C1',
  product: 'sigmet',
  tags: ['va', 'no_va_exp', 'sigmet', 'v1', 'c1'],
};

const METAR_ONLY: LintIssueCatalogEntry = {
  code: 'MISSING_TERMINATOR',
  severity: 'info',
  message_template: "Reports in bulletins end with '='",
  product: null,
  tags: ['terminator', 'metar', 'speci'],
};

const ENTRIES = [SIGMET_ONLY, VA_TAGGED, METAR_ONLY];

async function openCatalog(user: ReturnType<typeof userEvent.setup>) {
  render(<WorkbenchConsole defaultOpen lines={[]} catalogEntries={ENTRIES} />);
  await user.click(screen.getByTestId('lint-issue-catalog-toggle'));
  return screen.getByTestId('lint-issue-catalog-list');
}

describe('WorkbenchConsole catalog SIGMET/VA tags (T5.1 / E19-17)', () => {
  it('shows tags (and product when set) in catalog list copy for SIGMET rows', async () => {
    const user = userEvent.setup();
    const list = await openCatalog(user);

    const cnl = within(list).getByTestId('lint-issue-catalog-entry-SIGMET_CNL');
    expect(cnl).toHaveTextContent('SIGMET_CNL');
    expect(cnl).toHaveTextContent(/sigmet/);
    expect(cnl).toHaveTextContent(/product:\s*sigmet/i);

    const noVa = within(list).getByTestId('lint-issue-catalog-entry-NO_VA_EXP');
    expect(noVa).toHaveTextContent(/va/);
    expect(noVa).toHaveTextContent(/sigmet/);
  });

  it('filters the catalog list to sigmet-tagged rows via tag filter', async () => {
    const user = userEvent.setup();
    await openCatalog(user);

    const filter = screen.getByTestId('lint-issue-catalog-tag-filter');
    await user.selectOptions(filter, 'sigmet');

    const list = screen.getByTestId('lint-issue-catalog-list');
    expect(
      within(list).getByTestId('lint-issue-catalog-entry-SIGMET_CNL'),
    ).toBeInTheDocument();
    expect(
      within(list).getByTestId('lint-issue-catalog-entry-NO_VA_EXP'),
    ).toBeInTheDocument();
    expect(
      within(list).queryByTestId('lint-issue-catalog-entry-MISSING_TERMINATOR'),
    ).not.toBeInTheDocument();

    expect(screen.getByTestId('lint-issue-catalog-toggle')).toHaveTextContent(/2/);
  });

  it('filters the catalog list to va-tagged rows via tag filter', async () => {
    const user = userEvent.setup();
    await openCatalog(user);

    const filter = screen.getByTestId('lint-issue-catalog-tag-filter');
    await user.selectOptions(filter, 'va');

    const list = screen.getByTestId('lint-issue-catalog-list');
    expect(
      within(list).getByTestId('lint-issue-catalog-entry-NO_VA_EXP'),
    ).toBeInTheDocument();
    expect(
      within(list).queryByTestId('lint-issue-catalog-entry-SIGMET_CNL'),
    ).not.toBeInTheDocument();
    expect(
      within(list).queryByTestId('lint-issue-catalog-entry-MISSING_TERMINATOR'),
    ).not.toBeInTheDocument();

    expect(screen.getByTestId('lint-issue-catalog-toggle')).toHaveTextContent(/1/);
  });

  it('exposes sigmet and va in the tag filter options', async () => {
    const user = userEvent.setup();
    await openCatalog(user);

    const filter = screen.getByTestId('lint-issue-catalog-tag-filter');
    const options = within(filter)
      .getAllByRole('option')
      .map((el) => el.getAttribute('value'));
    expect(options).toContain('sigmet');
    expect(options).toContain('va');
  });
});
