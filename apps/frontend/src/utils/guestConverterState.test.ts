import { describe, it, expect, beforeEach } from 'vitest';
import {
  clearGuestConverterState,
  readGuestConverterState,
  saveGuestConverterState,
} from './guestConverterState';

describe('guestConverterState', () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  it('round-trips converter snapshot through sessionStorage', () => {
    const snapshot = {
      manualInput: 'METAR TEST',
      pendingFiles: [],
      convertedFiles: [],
      conversionLog: null,
      conversionParams: {},
    };

    saveGuestConverterState(snapshot);
    expect(readGuestConverterState()).toEqual(snapshot);
  });

  it('returns null when no guest state is stored', () => {
    expect(readGuestConverterState()).toBeNull();
  });

  it('clears stored guest state', () => {
    saveGuestConverterState({
      manualInput: 'x',
      pendingFiles: [],
      convertedFiles: [],
      conversionLog: null,
      conversionParams: {},
    });
    clearGuestConverterState();
    expect(readGuestConverterState()).toBeNull();
  });

  it('returns null for invalid JSON', () => {
    sessionStorage.setItem('metar_guest_converter_state', 'not-json');
    expect(readGuestConverterState()).toBeNull();
  });
});
