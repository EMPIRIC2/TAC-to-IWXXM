/**
 * Drawer + product heading permutations for Live decode current time.
 */

import { describe, expect, it, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { ConvertResultsDrawer } from './ConvertResultsDrawer';
import { DecodePanel } from './DecodePanel';

const segments = [{ start: 0, end: 6, code: 'SIGMET', explanation: 'Report type' }];

const drawerBodies = {
  iwxxm: <div>iwxxm</div>,
  console: <div>console</div>,
  downloads: <div>downloads</div>,
};

describe('live decode current time in Results drawer', () => {
  it.each(['SIGMET', 'METAR', 'TAF', 'SPECI'] as const)(
    'pinned Live decode (%s) shows spaced heading and clock when decoder open',
    (product) => {
      render(
        <ConvertResultsDrawer
          open
          onOpenChange={() => undefined}
          tab="decoder"
          onTabChange={() => undefined}
          height={320}
          onHeightChange={() => undefined}
          {...drawerBodies}
          decoder={
            <DecodePanel pinned product={product} segments={segments} residuals={[]} />
          }
        />,
      );

      const chrome = screen.getByTestId('convert-results-drawer-chrome');
      expect(within(chrome).getByText('Results')).toBeVisible();

      const heading = screen.getByTestId('live-decode-heading');
      expect(heading).toHaveTextContent(`Live decode (${product})`);
      // Explicit space before paren — not Live decode(PRODUCT)
      expect(heading.textContent).toMatch(/Live decode \(/);

      expect(screen.getByTestId('decode-segments')).toBeInTheDocument();
      expect(screen.getByTestId('live-decode-current-time')).toBeInTheDocument();
      expect(screen.getByTestId('live-decode-current-time').textContent).toContain(
        'UTC',
      );
      expect(screen.getByTestId('live-decode-current-time-toggle')).toBeChecked();
    },
  );

  it('hides decoder clock when Results drawer closed (delete/hide mutation)', () => {
    const { rerender } = render(
      <ConvertResultsDrawer
        open
        onOpenChange={() => undefined}
        tab="decoder"
        onTabChange={() => undefined}
        height={320}
        onHeightChange={() => undefined}
        {...drawerBodies}
        decoder={
          <DecodePanel pinned product="SIGMET" segments={segments} residuals={[]} />
        }
      />,
    );
    expect(screen.getByTestId('live-decode-current-time')).toBeVisible();

    rerender(
      <ConvertResultsDrawer
        open={false}
        onOpenChange={() => undefined}
        tab="decoder"
        onTabChange={() => undefined}
        height={320}
        onHeightChange={() => undefined}
        {...drawerBodies}
        decoder={
          <DecodePanel pinned product="SIGMET" segments={segments} residuals={[]} />
        }
      />,
    );
    expect(screen.getByTestId('convert-results-drawer')).toHaveAttribute(
      'data-open',
      'false',
    );
    expect(screen.getByTestId('convert-results-tabs')).not.toBeVisible();
  });

  it('Show control re-opens drawer with clock still present (create after hide)', async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();
    render(
      <ConvertResultsDrawer
        open={false}
        onOpenChange={onOpenChange}
        tab="decoder"
        onTabChange={() => undefined}
        height={320}
        onHeightChange={() => undefined}
        {...drawerBodies}
        decoder={
          <DecodePanel pinned product="METAR" segments={segments} residuals={[]} />
        }
      />,
    );
    await user.click(screen.getByTestId('convert-results-drawer-toggle'));
    expect(onOpenChange).toHaveBeenCalledWith(true);
  });

  it('collapsible Decode (non-pinned) does not show Live decode clock', async () => {
    const user = userEvent.setup();
    render(
      <DecodePanel product="SIGMET" defaultOpen segments={segments} residuals={[]} />,
    );
    expect(screen.queryByTestId('live-decode-current-time')).not.toBeInTheDocument();
    expect(screen.queryByTestId('live-decode-heading')).not.toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /Decode/i }));
    expect(screen.queryByTestId('live-decode-current-time')).not.toBeInTheDocument();
  });
});
