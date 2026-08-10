/**
 * EV-053 branch fill — catalog overflow copy (WorkbenchConsole.tsx:242).
 */

import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { WorkbenchConsole } from './WorkbenchConsole';
import type { LintIssueCatalogEntry } from '@/utils/api';

vi.mock('/utils/convertParams', () => ({
  consoleLevelPasses: () => true,
}));

const makeEntry = (index: number): LintIssueCatalogEntry => ({
  code: `CODE_${index}`,
  severity: 'info',
  message_template: `Message ${index}`,
  product: null,
  tags: [`tag-${index % 3}`],
});

describe('WorkbenchConsole catalog overflow (EV-053)', () => {
  it('truncates the catalog list after 80 rows and shows overflow copy', async () => {
    const user = userEvent.setup();
    render(
      <WorkbenchConsole
        defaultOpen
        lines={[]}
        catalogEntries={Array.from({ length: 81 }, (_, index) => makeEntry(index))}
      />,
    );

    await user.click(screen.getByTestId('lint-issue-catalog-toggle'));
    expect(screen.getByTestId('lint-issue-catalog-list')).toHaveTextContent(
      /…and 1 more/i,
    );
  });

  it('builds tag options when catalog entries omit tags', async () => {
    const user = userEvent.setup();
    const untagged = {
      code: 'UNTAGGED',
      severity: 'info',
      message_template: 'No tags here',
      product: null,
    } as unknown as LintIssueCatalogEntry;

    render(
      <WorkbenchConsole
        defaultOpen
        lines={[]}
        catalogEntries={[untagged, makeEntry(1)]}
      />,
    );

    await user.click(screen.getByTestId('lint-issue-catalog-toggle'));
    const filter = screen.getByTestId('lint-issue-catalog-tag-filter');
    const values = Array.from(filter.querySelectorAll('option')).map((option) =>
      option.getAttribute('value'),
    );
    expect(values).toContain('');
    expect(values.some((value) => value && value.length > 0)).toBe(true);
  });
});
