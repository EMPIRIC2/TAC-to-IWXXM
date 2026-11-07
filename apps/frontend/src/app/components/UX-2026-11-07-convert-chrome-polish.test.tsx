/**
 * UX-2026-11-07-convert-chrome-polish — convert chrome polish regressions.
 *
 * [Corpus: ui-style] [Corpus: tests]
 */

import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { ConvertSettingsCog } from './ConvertSettingsCog';
import { OperatorFooter } from './OperatorFooter';
import { deriveCalmConvertUi } from '@/utils/convertCalmState';
import { UserPreferencesDialog } from './UserPreferencesDialog';

vi.mock('sonner', () => ({
  toast: { error: vi.fn(), success: vi.fn() },
}));

describe('UX-2026-11-07-convert-chrome-polish', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('empty calm phase keeps bordered converter chrome (no marketing hero flag)', () => {
    const ui = deriveCalmConvertUi({ hasInput: false, hasConverted: false });
    expect(ui.phase).toBe('empty');
    expect(ui.showEmptyHero).toBe(false);
  });

  it('settings cog exposes a slow-fade hover card (not title-only)', async () => {
    const user = userEvent.setup();
    render(
      <ConvertSettingsCog>
        <div>body</div>
      </ConvertSettingsCog>,
    );
    const cog = screen.getByTestId('convert-settings-cog');
    expect(cog).not.toHaveAttribute('title');
    const card = screen.getByTestId('icon-hover-card');
    expect(card).toHaveTextContent('Settings');
    expect(card.className).toMatch(/opacity-0/);
    expect(card.className).toMatch(/duration-500|duration-\[500ms\]|duration-700/);
    await user.hover(cog);
    expect(card).toBeInTheDocument();
  });

  it('operator footer is full-bleed and collapses to a right-edge reveal bar', async () => {
    const user = userEvent.setup();
    render(<OperatorFooter onOpenPrivacy={vi.fn()} onOpenTerms={vi.fn()} />);

    const footer = screen.getByTestId('operator-footer');
    expect(footer.className).toMatch(/\bw-full\b|\binset-x-0\b|\bleft-0\b/);
    expect(footer.className).toMatch(/\bbottom-0\b|\bfixed\b|\bsticky\b/);

    await user.click(screen.getByTestId('operator-footer-collapse'));
    expect(screen.queryByTestId('operator-footer')).not.toBeInTheDocument();
    const reveal = screen.getByTestId('operator-footer-reveal');
    expect(reveal.className).toMatch(/\bright-0\b/);
    await user.click(reveal);
    expect(screen.getByTestId('operator-footer')).toBeInTheDocument();
  });

  it('output-extension select caret is nudged left via custom background position', () => {
    render(
      <UserPreferencesDialog
        isOpen
        onClose={() => undefined}
        userEmail="ada@example.com"
      />,
    );
    const select = screen.getByLabelText('Output file extension');
    expect(select.id).toBe('output-extension');
    expect(select.className).toMatch(/appearance-none/);
    expect(select.className).toMatch(/bg-\[position:|bg-no-repeat/);
  });
});

describe('UX-2026-11-07 toolbar helpers (layout contracts)', () => {
  it('documents rightmost settings + always-visible product via testids on a stub toolbar', () => {
    render(
      <div data-testid="convert-chrome-toolbar" className="flex justify-between">
        <div data-testid="convert-chrome-toolbar-start">
          <select
            data-testid="product-type-select"
            aria-label="Product"
            defaultValue="auto"
          >
            <option value="auto">Auto-detect</option>
          </select>
        </div>
        <div data-testid="convert-chrome-toolbar-end">
          <ConvertSettingsCog>
            <div>advanced</div>
          </ConvertSettingsCog>
        </div>
      </div>,
    );
    const toolbar = screen.getByTestId('convert-chrome-toolbar');
    const product = within(toolbar).getByTestId('product-type-select');
    const cog = within(toolbar).getByTestId('convert-settings-cog');
    const start = within(toolbar).getByTestId('convert-chrome-toolbar-start');
    const end = within(toolbar).getByTestId('convert-chrome-toolbar-end');
    expect(start).toContainElement(product);
    expect(end).toContainElement(cog);
    expect(
      Boolean(start.compareDocumentPosition(end) & Node.DOCUMENT_POSITION_FOLLOWING),
    ).toBe(true);
  });
});
