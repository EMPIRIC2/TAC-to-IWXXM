import { beforeEach, describe, expect, it } from 'vitest';
import {
  GLOSSARY_PREFS_STORAGE_KEY,
  isGlossaryHoverEnabled,
} from './glossaryHoverPrefs';

describe('glossaryHoverPrefs (TC-F38-004)', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('defaults to ON when prefs are missing', () => {
    expect(isGlossaryHoverEnabled()).toBe(true);
  });

  it('defaults to ON when key is omitted', () => {
    localStorage.setItem(
      GLOSSARY_PREFS_STORAGE_KEY,
      JSON.stringify({ displayName: 'Ops' }),
    );
    expect(isGlossaryHoverEnabled()).toBe(true);
  });

  it('returns false when user opted out', () => {
    localStorage.setItem(
      GLOSSARY_PREFS_STORAGE_KEY,
      JSON.stringify({ glossaryHoverEnabled: false }),
    );
    expect(isGlossaryHoverEnabled()).toBe(false);
  });

  it('returns true on invalid JSON', () => {
    localStorage.setItem(GLOSSARY_PREFS_STORAGE_KEY, '{not-json');
    expect(isGlossaryHoverEnabled()).toBe(true);
  });

  it('treats explicit true as enabled (validation mode)', () => {
    localStorage.setItem(
      GLOSSARY_PREFS_STORAGE_KEY,
      JSON.stringify({ glossaryHoverEnabled: true }),
    );
    expect(isGlossaryHoverEnabled()).toBe(true);
  });
});
