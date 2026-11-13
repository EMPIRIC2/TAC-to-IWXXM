/**
 * GlossaryScope prefs reactivity (TC-F38-004).
 */

import { act, render, renderHook, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { GLOSSARY_PREFS_STORAGE_KEY } from '@/utils/glossaryHoverPrefs';
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

  it('useGlossaryScope outside provider returns disabled no-op', () => {
    const { result } = renderHook(() => useGlossaryScope());
    expect(result.current.hoverEnabled).toBe(false);
    expect(result.current.openGlossaryEntry('sigmet')).toBeUndefined();
  });

  it('reacts to storage events for glossary prefs key and clear', () => {
    localStorage.setItem(
      GLOSSARY_PREFS_STORAGE_KEY,
      JSON.stringify({ glossaryHoverEnabled: true }),
    );
    render(
      <GlossaryScope openGlossaryEntry={() => undefined}>
        <GlossaryRichText text="SIGMET nearby" />
      </GlossaryScope>,
    );
    expect(screen.getByTestId('glossary-term-sigmet')).toBeInTheDocument();

    localStorage.setItem(
      GLOSSARY_PREFS_STORAGE_KEY,
      JSON.stringify({ glossaryHoverEnabled: false }),
    );
    act(() => {
      window.dispatchEvent(
        new StorageEvent('storage', { key: GLOSSARY_PREFS_STORAGE_KEY }),
      );
    });
    expect(screen.queryByTestId('glossary-term-sigmet')).not.toBeInTheDocument();

    localStorage.setItem(
      GLOSSARY_PREFS_STORAGE_KEY,
      JSON.stringify({ glossaryHoverEnabled: true }),
    );
    act(() => {
      window.dispatchEvent(new StorageEvent('storage', { key: null }));
    });
    expect(screen.getByTestId('glossary-term-sigmet')).toBeInTheDocument();

    act(() => {
      window.dispatchEvent(new StorageEvent('storage', { key: 'unrelated-key' }));
    });
    expect(screen.getByTestId('glossary-term-sigmet')).toBeInTheDocument();
  });
});
