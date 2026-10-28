/**
 * TC-UX-DECLUTTER drawer chrome (UJ-089).
 *
 * [Corpus: tests §TC-UX-DECLUTTER]
 */

import { describe, expect, it, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { ConvertResultsDrawer } from './ConvertResultsDrawer';

describe('ConvertResultsDrawer', () => {
  it('TC-UX-DECLUTTER-001/002: one panel at a time when open', async () => {
    const user = userEvent.setup();
    const onTabChange = vi.fn();
    render(
      <ConvertResultsDrawer
        open
        onOpenChange={() => undefined}
        tab="iwxxm"
        onTabChange={onTabChange}
        iwxxm={<div>iwxxm-body</div>}
        console={<div>console-body</div>}
        decoder={<div>decoder-body</div>}
        map={<div>map-body</div>}
        downloads={<div>downloads-body</div>}
      />,
    );

    const drawer = screen.getByTestId('convert-results-drawer');
    expect(drawer).toHaveAttribute('data-open', 'true');
    expect(within(drawer).getByText('iwxxm-body')).toBeVisible();
    expect(within(drawer).getByText('console-body')).not.toBeVisible();

    await user.click(screen.getByTestId('convert-results-tab-console'));
    expect(onTabChange).toHaveBeenCalledWith('console');
  });

  it('collapses tab chrome when closed', () => {
    render(
      <ConvertResultsDrawer
        open={false}
        onOpenChange={() => undefined}
        tab="iwxxm"
        onTabChange={() => undefined}
        iwxxm={<div>iwxxm-body</div>}
        console={<div>console-body</div>}
        decoder={<div>decoder-body</div>}
        map={<div>map-body</div>}
        downloads={<div>downloads-body</div>}
      />,
    );
    expect(screen.getByTestId('convert-results-drawer')).toHaveAttribute(
      'data-open',
      'false',
    );
    expect(screen.getByTestId('convert-results-tabs')).not.toBeVisible();
  });

  it('toggles open via Hide/Show control', async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();
    render(
      <ConvertResultsDrawer
        open
        onOpenChange={onOpenChange}
        tab="iwxxm"
        onTabChange={() => undefined}
        iwxxm={<div>iwxxm-body</div>}
        console={<div>console-body</div>}
        decoder={<div>decoder-body</div>}
        map={<div>map-body</div>}
        downloads={<div>downloads-body</div>}
      />,
    );
    await user.click(screen.getByTestId('convert-results-drawer-toggle'));
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });
});
