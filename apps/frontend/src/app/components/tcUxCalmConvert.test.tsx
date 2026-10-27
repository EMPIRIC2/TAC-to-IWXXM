/**
 * TC-UX-CALM-001..010 — Calmer Convert chrome regressions.
 *
 * [Corpus: tests] [Corpus: journeys §UJ-088]
 */

import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi, beforeEach } from 'vitest';

import { CalmConvertEmptyHero } from './CalmConvertEmptyHero';
import { ConvertHelpChecklist } from './ConvertHelpChecklist';
import { ConvertProfileDrawer } from './ConvertProfileDrawer';
import { ConvertValidityStrip } from './ConvertValidityStrip';
import { findInternalDocRefs } from '@/utils/internalDocRefGuard';

vi.mock('/utils/operatorHelp', () => ({
  OPERATOR_ONE_PAGER_URL: 'https://example.test/one-pager.md',
  OPERATOR_HANDBOOK_URL: 'https://example.test/handbook.md',
}));

describe('TC-UX-CALM leaf components', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('TC-UX-CALM-004: empty hero exposes one primary CTA and example chips', () => {
    render(
      <CalmConvertEmptyHero
        convertDisabled={false}
        isConverting={false}
        onConvert={() => undefined}
        exampleChips={[
          { id: 'm', label: 'METAR' },
          { id: 't', label: 'TAF' },
        ]}
        onExampleChip={() => undefined}
        profileLabel="United States (FAA/NWS)"
        onChangeProfile={() => undefined}
      >
        <textarea aria-label="TAC" />
      </CalmConvertEmptyHero>,
    );
    expect(screen.getByTestId('convert-empty-hero')).toBeInTheDocument();
    expect(screen.getByTestId('convert-primary-cta')).toHaveTextContent(
      'Convert & validate',
    );
    expect(screen.getByTestId('convert-example-chips')).toBeInTheDocument();
  });

  it('TC-UX-CALM-008: Help checklist opens, dismisses, and keeps one-pager link', async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();
    const { rerender } = render(
      <ConvertHelpChecklist open onOpenChange={onOpenChange} />,
    );
    const dialog = screen.getByTestId('convert-help-checklist');
    expect(dialog).toBeInTheDocument();
    expect(within(dialog).getByTestId('operator-help-link')).toHaveAttribute(
      'href',
      'https://example.test/one-pager.md',
    );
    await user.click(screen.getByRole('button', { name: 'Got it' }));
    expect(onOpenChange).toHaveBeenCalledWith(false);
    rerender(<ConvertHelpChecklist open={false} onOpenChange={onOpenChange} />);
    expect(screen.queryByTestId('convert-help-checklist')).not.toBeInTheDocument();
  });

  it('TC-UX-CALM-005: profile drawer has Apply and collapsed output options', () => {
    render(
      <ConvertProfileDrawer
        open
        onOpenChange={() => undefined}
        nationalSection={<div>national</div>}
        customizeSection={<div>customize</div>}
        outputSection={<div data-testid="output-body">output</div>}
        onApply={() => undefined}
      />,
    );
    const drawer = screen.getByTestId('convert-profile-drawer');
    expect(drawer).toBeInTheDocument();
    expect(screen.getByTestId('convert-profile-apply')).toBeInTheDocument();
    const outputDetails = screen.getByText('Output options').closest('details');
    expect(outputDetails).not.toHaveAttribute('open');
  });

  it('TC-UX-CALM-010: validity strip is present for success', () => {
    render(<ConvertValidityStrip notesCount={6} onNotesClick={() => undefined} />);
    expect(screen.getByTestId('convert-validity-strip')).toHaveTextContent(
      'Valid IWXXM bulletin, ready to send',
    );
  });

  it('TC-UX-CALM-009: calm copy has no internal planning vocabulary', () => {
    const copy = [
      'Convert a TAC report to IWXXM',
      'Convert & validate',
      'Download IWXXM',
      'Convert checklist',
      'Valid IWXXM bulletin, ready to send',
    ];
    for (const text of copy) {
      expect(findInternalDocRefs(text)).toEqual([]);
    }
  });
});
