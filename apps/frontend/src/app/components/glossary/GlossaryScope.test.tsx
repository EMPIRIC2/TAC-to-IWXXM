/**
 * GlossaryScope prefs reactivity (TC-F38-004).
 */

import { act, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { GlossaryRichText } from './GlossaryRichText';
import { GlossaryScope, notifyGlossaryPrefsChanged } from './GlossaryScope';

describe('GlossaryScope (TC-F38-004)', () => {
  it('disables marks after notify when prefs opt out', () => {
    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({ glossaryHoverEnabled: true }),
    );
    render(
      <GlossaryScope openGlossaryEntry={() => undefined}>
        <GlossaryRichText text="SIGMET nearby" />
      </GlossaryScope>,
    );
    expect(screen.getByTestId('glossary-term-sigmet')).toBeInTheDocument();

    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({ glossaryHoverEnabled: false }),
    );
    act(() => {
      notifyGlossaryPrefsChanged();
    });
    expect(screen.queryByTestId('glossary-term-sigmet')).not.toBeInTheDocument();
    expect(screen.getByText('SIGMET nearby')).toBeInTheDocument();
  });
});
