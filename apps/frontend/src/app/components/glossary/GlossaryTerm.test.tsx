import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { getAnnex3GlossaryEntry } from '@/data/annex3Glossary';
import { GlossaryScope } from './GlossaryScope';
import { GlossaryTerm } from './GlossaryTerm';
import { GlossaryRichText } from './GlossaryRichText';

const entry = getAnnex3GlossaryEntry('sigmet')!;

describe('GlossaryTerm (TC-F38-002 / TC-F38-005)', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('opens tip after 2s hover delay and links to Glossary', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    const openGlossaryEntry = vi.fn();
    render(
      <GlossaryScope openGlossaryEntry={openGlossaryEntry}>
        <GlossaryTerm entry={entry}>SIGMET</GlossaryTerm>
      </GlossaryScope>,
    );

    const trigger = screen.getByTestId('glossary-term-sigmet');
    await user.hover(trigger);
    expect(screen.queryByTestId('glossary-tip-sigmet')).not.toBeInTheDocument();

    await act(async () => {
      vi.advanceTimersByTime(2000);
    });

    expect(await screen.findByTestId('glossary-tip-sigmet')).toBeInTheDocument();
    await user.click(screen.getByTestId('glossary-open-sigmet'));
    expect(openGlossaryEntry).toHaveBeenCalledWith('sigmet');
  });

  it('opens tip via keyboard Enter (a11y twin)', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(
      <GlossaryScope openGlossaryEntry={() => undefined}>
        <GlossaryTerm entry={entry}>SIGMET</GlossaryTerm>
      </GlossaryScope>,
    );
    const trigger = screen.getByTestId('glossary-term-sigmet');
    trigger.focus();
    await user.keyboard('{Enter}');
    expect(await screen.findByTestId('glossary-tip-sigmet')).toBeInTheDocument();
  });

  it('renders plain text when hover prefs are off', () => {
    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({ glossaryHoverEnabled: false }),
    );
    render(
      <GlossaryScope openGlossaryEntry={() => undefined}>
        <GlossaryRichText text="A SIGMET warning" />
      </GlossaryScope>,
    );
    expect(screen.queryByTestId('glossary-term-sigmet')).not.toBeInTheDocument();
    expect(screen.getByText('A SIGMET warning')).toBeInTheDocument();
  });

  it('GlossaryTerm itself skips tip chrome when prefs are off', () => {
    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({ glossaryHoverEnabled: false }),
    );
    render(
      <GlossaryScope openGlossaryEntry={() => undefined}>
        <GlossaryTerm entry={entry}>SIGMET</GlossaryTerm>
      </GlossaryScope>,
    );
    expect(screen.queryByTestId('glossary-term-sigmet')).not.toBeInTheDocument();
    expect(screen.getByText('SIGMET')).toBeInTheDocument();
  });

  it('does not open tip when hover ends before 2s (TC-F38-002 failure)', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(
      <GlossaryScope openGlossaryEntry={() => undefined}>
        <GlossaryTerm entry={entry}>SIGMET</GlossaryTerm>
      </GlossaryScope>,
    );
    const trigger = screen.getByTestId('glossary-term-sigmet');
    await user.hover(trigger);
    await act(async () => {
      vi.advanceTimersByTime(1500);
    });
    await user.unhover(trigger);
    await act(async () => {
      vi.advanceTimersByTime(1000);
    });
    expect(screen.queryByTestId('glossary-tip-sigmet')).not.toBeInTheDocument();
  });

  it('closes tip on Escape (TC-F38-005 failure)', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(
      <GlossaryScope openGlossaryEntry={() => undefined}>
        <GlossaryTerm entry={entry}>SIGMET</GlossaryTerm>
      </GlossaryScope>,
    );
    const trigger = screen.getByTestId('glossary-term-sigmet');
    trigger.focus();
    await user.keyboard('{Enter}');
    expect(await screen.findByTestId('glossary-tip-sigmet')).toBeInTheDocument();
    await user.keyboard('{Escape}');
    expect(screen.queryByTestId('glossary-tip-sigmet')).not.toBeInTheDocument();
  });
});
