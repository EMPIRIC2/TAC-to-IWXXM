/**
 * F38 parameterized battery — success / failure / validation modes.
 */
import { beforeEach, describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Annex3GlossaryPage } from '../Annex3GlossaryPage';
import {
  isLimitedMeaningHoverExcluded,
  segmentGlossaryText,
} from '@/utils/annex3GlossaryMatch';
import {
  GLOSSARY_PREFS_STORAGE_KEY,
  isGlossaryHoverEnabled,
} from '@/utils/glossaryHoverPrefs';
import { GlossaryScope } from './GlossaryScope';

describe.each([
  {
    mode: 'success' as const,
    query: 'SIGMET',
    expectSigmet: true,
    expectEmptyHint: false,
  },
  {
    mode: 'failure' as const,
    query: 'zzzz-no-match-xyz',
    expectSigmet: false,
    expectEmptyHint: true,
  },
  {
    mode: 'validation' as const,
    query: '  sigmet  ',
    expectSigmet: true,
    expectEmptyHint: false,
  },
])('Annex3GlossaryPage search ($mode)', ({ query, expectSigmet, expectEmptyHint }) => {
  it(`filters glossary entries in ${expectSigmet ? 'hit' : 'miss'} mode`, async () => {
    const user = userEvent.setup();
    render(
      <GlossaryScope openGlossaryEntry={() => undefined}>
        <Annex3GlossaryPage />
      </GlossaryScope>,
    );
    await expect(screen.findByTestId('glossary-entry-sigmet')).resolves.toBeTruthy();
    await user.clear(screen.getByTestId('glossary-search'));
    await user.type(screen.getByTestId('glossary-search'), query);
    if (expectSigmet) {
      expect(screen.getByTestId('glossary-entry-sigmet')).toBeInTheDocument();
    } else {
      expect(screen.queryByTestId('glossary-entry-sigmet')).not.toBeInTheDocument();
    }
    if (expectEmptyHint) {
      expect(screen.getByTestId('glossary-entry-list')).toBeInTheDocument();
    }
  });
});

describe.each([
  {
    mode: 'success' as const,
    stored: undefined,
    enabled: true,
  },
  {
    mode: 'failure' as const,
    stored: { glossaryHoverEnabled: false },
    enabled: false,
  },
  {
    mode: 'validation' as const,
    stored: { glossaryHoverEnabled: 'yes' },
    enabled: true,
  },
])('glossaryHoverPrefs ($mode)', ({ stored, enabled }) => {
  beforeEach(() => {
    localStorage.clear();
  });

  it(`resolves hover enabled=${String(enabled)}`, () => {
    if (stored !== undefined) {
      localStorage.setItem(GLOSSARY_PREFS_STORAGE_KEY, JSON.stringify(stored));
    }
    expect(isGlossaryHoverEnabled()).toBe(enabled);
  });
});

describe.each([
  {
    mode: 'success' as const,
    text: 'SIGMET and aerodrome',
    expectTerms: ['sigmet', 'aerodrome'],
  },
  {
    mode: 'failure' as const,
    text: 'provide issue supply',
    expectTerms: [] as string[],
  },
  {
    mode: 'validation' as const,
    text: '',
    expectTerms: [] as string[],
  },
])('annex3GlossaryMatch ($mode)', ({ text, expectTerms }) => {
  it('segments text for the mode', () => {
    const terms = segmentGlossaryText(text)
      .filter((s) => s.kind === 'term')
      .map((s) => (s.kind === 'term' ? s.entry.id : ''));
    expect(terms).toEqual(expectTerms);
    if (text.includes('provide')) {
      expect(isLimitedMeaningHoverExcluded('provide')).toBe(true);
    }
  });
});
