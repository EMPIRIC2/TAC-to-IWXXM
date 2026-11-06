/**
 * Bulletin report picker.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { BulletinReportList } from './BulletinReportList';

describe('BulletinReportList', () => {
  it('selects a report and returns to the whole bulletin', async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    const onShowAll = vi.fn();
    render(
      <BulletinReportList
        reports={[
          { tac: 'METAR KJFK=', title: 'METAR KJFK=' },
          { tac: 'METAR KLAX=', title: 'METAR KLAX=' },
        ]}
        selectedIndex={1}
        onSelect={onSelect}
        onShowAll={onShowAll}
      />,
    );
    expect(screen.getByRole('button', { name: /Report 2 METAR KLAX/ })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    await user.click(screen.getByRole('button', { name: /Report 1 METAR KJFK/ }));
    expect(onSelect).toHaveBeenCalledWith(0, 'METAR KJFK=');
    await user.click(screen.getByRole('button', { name: 'Whole bulletin' }));
    expect(onShowAll).toHaveBeenCalled();
  });
});
