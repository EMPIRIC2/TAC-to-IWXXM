/**
 * GlossaryScope prefs reactivity (TC-F38-004).
 */

import { act, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { GlossaryRichText } from './GlossaryRichText';
import {
  GlossaryScope,
  notifyGlossaryPrefsChanged,
  useGlossaryScope,
} from './GlossaryScope';

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

  it('reacts to storage events for glossary prefs', () => {
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
      window.dispatchEvent(
        new StorageEvent('storage', {
          key: 'metar_converter_preferences',
          newValue: JSON.stringify({ glossaryHoverEnabled: false }),
        }),
      );
    });
    expect(screen.queryByTestId('glossary-term-sigmet')).not.toBeInTheDocument();

    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({ glossaryHoverEnabled: true }),
    );
    act(() => {
      window.dispatchEvent(new StorageEvent('storage', { key: null }));
    });
    expect(screen.getByTestId('glossary-term-sigmet')).toBeInTheDocument();
  });

  it('ignores unrelated storage keys', () => {
    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({ glossaryHoverEnabled: true }),
    );
    render(
      <GlossaryScope openGlossaryEntry={() => undefined}>
        <GlossaryRichText text="SIGMET nearby" />
      </GlossaryScope>,
    );
    act(() => {
      window.dispatchEvent(
        new StorageEvent('storage', { key: 'other-key', newValue: 'x' }),
      );
    });
    expect(screen.getByTestId('glossary-term-sigmet')).toBeInTheDocument();
  });

  it('useGlossaryScope outside provider is a disabled no-op', () => {
    function Probe() {
      const scope = useGlossaryScope();
      return (
        <button
          type="button"
          data-testid="outside-open"
          onClick={() => scope.openGlossaryEntry('sigmet')}
        >
          {String(scope.hoverEnabled)}
        </button>
      );
    }
    render(<Probe />);
    expect(screen.getByTestId('outside-open')).toHaveTextContent('false');
    act(() => {
      screen.getByTestId('outside-open').click();
    });
  });
});
