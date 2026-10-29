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

  it('TC-UX-CALM-004: empty hero exposes one primary CTA and example chips', async () => {
    const user = userEvent.setup();
    const onExampleChip = vi.fn();
    const onChangeProfile = vi.fn();
    const onOtherTask = vi.fn();
    const onConvert = vi.fn();
    render(
      <CalmConvertEmptyHero
        convertDisabled={false}
        isConverting={false}
        onConvert={onConvert}
        exampleChips={[
          { id: 'm', label: 'METAR' },
          { id: 't', label: 'TAF' },
        ]}
        onExampleChip={onExampleChip}
        profileLabel="United States (FAA/NWS)"
        onChangeProfile={onChangeProfile}
        onOtherTask={onOtherTask}
      >
        <textarea aria-label="TAC" />
      </CalmConvertEmptyHero>,
    );
    expect(screen.getByTestId('convert-empty-hero')).toBeInTheDocument();
    expect(screen.getByTestId('convert-primary-cta')).toHaveTextContent('Convert');
    expect(screen.getByTestId('convert-example-chips')).toBeInTheDocument();
    await user.click(screen.getByTestId('convert-example-chip-m'));
    expect(onExampleChip).toHaveBeenCalledWith('m');
    await user.click(screen.getByTestId('convert-primary-cta'));
    expect(onConvert).toHaveBeenCalled();
    await user.click(screen.getByTestId('convert-profile-change'));
    expect(onChangeProfile).toHaveBeenCalled();
    await user.click(
      screen.getByRole('button', { name: 'Convert a full bulletin (AHL)' }),
    );
    expect(onOtherTask).toHaveBeenCalledWith('ahl');
    await user.click(screen.getByRole('button', { name: 'Validate existing IWXXM' }));
    expect(onOtherTask).toHaveBeenCalledWith('validate_iwxxm');
    await user.click(screen.getByRole('button', { name: 'Build a COLLECT bundle' }));
    expect(onOtherTask).toHaveBeenCalledWith('collect');
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

  it('TC-UX-CALM-005: profile drawer has Apply and collapsed output options', async () => {
    const user = userEvent.setup();
    const onApply = vi.fn();
    const onOpenChange = vi.fn();
    const onReset = vi.fn();
    render(
      <ConvertProfileDrawer
        open
        onOpenChange={onOpenChange}
        nationalSection={<div>national</div>}
        customizeSection={<div>customize</div>}
        outputSection={<div data-testid="output-body">output</div>}
        onApply={onApply}
        onReset={onReset}
      />,
    );
    const drawer = screen.getByTestId('convert-profile-drawer');
    expect(drawer).toBeInTheDocument();
    expect(screen.getByTestId('convert-profile-apply')).toBeInTheDocument();
    const outputDetails = screen.getByText('Output options').closest('details');
    expect(outputDetails).not.toHaveAttribute('open');
    await user.click(screen.getByRole('button', { name: 'Reset to WMO defaults' }));
    expect(onReset).toHaveBeenCalled();
    await user.click(screen.getByTestId('convert-profile-apply'));
    expect(onApply).toHaveBeenCalled();
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it('TC-UX-CALM-010: validity strip is present for success', async () => {
    const user = userEvent.setup();
    const onNotesClick = vi.fn();
    render(<ConvertValidityStrip notesCount={6} onNotesClick={onNotesClick} />);
    expect(screen.getByTestId('convert-validity-strip')).toHaveTextContent(
      'Valid IWXXM bulletin, ready to send',
    );
    await user.click(screen.getByRole('button', { name: '6 notes' }));
    expect(onNotesClick).toHaveBeenCalled();
  });

  it('TC-UX-CALM-010: omits notes control without handler or zero notes', () => {
    const { rerender } = render(<ConvertValidityStrip notesCount={3} />);
    expect(screen.queryByRole('button', { name: /notes/i })).not.toBeInTheDocument();
    rerender(<ConvertValidityStrip notesCount={0} onNotesClick={() => undefined} />);
    expect(screen.queryByRole('button', { name: /notes/i })).not.toBeInTheDocument();
  });

  it('covers optional hero/drawer branches without other-task or reset', () => {
    render(
      <CalmConvertEmptyHero
        convertDisabled
        isConverting
        onConvert={() => undefined}
        exampleChips={[]}
        onExampleChip={() => undefined}
        profileLabel="WMO"
        onChangeProfile={() => undefined}
      >
        <span>input</span>
      </CalmConvertEmptyHero>,
    );
    expect(
      screen.queryByRole('button', { name: 'Convert a full bulletin (AHL)' }),
    ).not.toBeInTheDocument();

    render(
      <ConvertProfileDrawer
        open
        onOpenChange={() => undefined}
        nationalSection={<div>n</div>}
        customizeSection={<div>c</div>}
        outputSection={<div>o</div>}
        onApply={() => undefined}
      />,
    );
    expect(
      screen.queryByRole('button', { name: 'Reset to WMO defaults' }),
    ).not.toBeInTheDocument();
  });

  it('TC-UX-CALM-009: calm copy has no internal planning vocabulary', () => {
    const copy = [
      'Convert a TAC report to IWXXM',
      'Convert',
      'Download latest',
      'Convert checklist',
      'Valid IWXXM bulletin, ready to send',
    ];
    for (const text of copy) {
      expect(findInternalDocRefs(text)).toEqual([]);
    }
  });
});
