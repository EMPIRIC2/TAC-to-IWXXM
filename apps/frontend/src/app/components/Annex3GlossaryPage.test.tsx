import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Annex3GlossaryPage } from './Annex3GlossaryPage';
import { GlossaryScope } from './glossary/GlossaryScope';
import { ANNEX3_GLOSSARY_CITATION } from '@/data/annex3Glossary';

function renderPage(focusTermId?: string | null) {
  return render(
    <GlossaryScope openGlossaryEntry={() => undefined}>
      <Annex3GlossaryPage focusTermId={focusTermId ?? null} />
    </GlossaryScope>,
  );
}

describe('Annex3GlossaryPage (TC-F38-001 / TC-F38-007)', () => {
  it('renders citation, beta badge, and seeded entries', () => {
    renderPage();
    expect(screen.getByTestId('annex3-glossary-page')).toBeInTheDocument();
    expect(screen.getByTestId('glossary-beta-badge')).toHaveTextContent('Beta');
    expect(screen.getByTestId('glossary-citation')).toHaveTextContent(
      ANNEX3_GLOSSARY_CITATION,
    );
    expect(screen.getByTestId('glossary-entry-sigmet')).toBeInTheDocument();
    const limited = screen.getByTestId('glossary-limited-meaning');
    expect(limited).toBeInTheDocument();
    expect(limited.textContent).toMatch(/provide/i);
    expect(limited.textContent).toMatch(/issue/i);
    expect(limited.textContent).toMatch(/supply/i);
  });

  it('filters entries by search', async () => {
    const user = userEvent.setup();
    renderPage();
    await user.type(screen.getByTestId('glossary-search'), 'SIGMET');
    expect(screen.getByTestId('glossary-entry-sigmet')).toBeInTheDocument();
    expect(screen.queryByTestId('glossary-entry-aerodrome')).not.toBeInTheDocument();
  });

  it('does not embed substantial verbatim Annex dump markers', () => {
    renderPage();
    const page = screen.getByTestId('annex3-glossary-page').textContent ?? '';
    expect(page).not.toMatch(/Chapter 1\.\s*Definitions/i);
    expect(page.toLowerCase()).toContain('paraphrases');
  });
});

describe('Annex3GlossaryPage focus (UJ-GLOSS-001)', () => {
  it('invokes onFocusHandled when focusTermId is set', () => {
    const onFocusHandled = vi.fn();
    const scrollIntoView = vi.fn();
    Element.prototype.scrollIntoView = scrollIntoView;
    render(
      <GlossaryScope openGlossaryEntry={() => undefined}>
        <Annex3GlossaryPage focusTermId="rvr" onFocusHandled={onFocusHandled} />
      </GlossaryScope>,
    );
    expect(onFocusHandled).toHaveBeenCalled();
  });

  it('still calls onFocusHandled when focusTermId is missing (failure)', () => {
    const onFocusHandled = vi.fn();
    render(
      <GlossaryScope openGlossaryEntry={() => undefined}>
        <Annex3GlossaryPage
          focusTermId="missing-term"
          onFocusHandled={onFocusHandled}
        />
      </GlossaryScope>,
    );
    expect(onFocusHandled).toHaveBeenCalled();
    expect(screen.queryByTestId('glossary-entry-missing-term')).not.toBeInTheDocument();
  });
});

describe('Annex3GlossaryPage search failure (TC-F38-001)', () => {
  it('shows empty state when search matches nothing', async () => {
    const user = userEvent.setup();
    renderPage();
    await user.type(screen.getByTestId('glossary-search'), 'zzzz-no-match');
    expect(screen.queryByTestId('glossary-entry-sigmet')).not.toBeInTheDocument();
    expect(screen.getByTestId('annex3-glossary-page')).toBeInTheDocument();
  });
});
