/**
 * Live decode current-time formatter + prefs (success / failure / validation).
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import {
  LIVE_DECODE_SHOW_CURRENT_TIME_KEY,
  formatLiveDecodeCurrentTime,
  readShowLiveDecodeCurrentTime,
  writeShowLiveDecodeCurrentTime,
} from './liveDecodeCurrentTime';

describe('formatLiveDecodeCurrentTime', () => {
  it('formats local + UTC with zone marker (validation success)', () => {
    const fixed = new Date('2026-11-13T20:23:00.000Z');
    const parts = formatLiveDecodeCurrentTime(fixed, 'America/New_York');
    expect(parts.label).toMatch(/^Now: /);
    expect(parts.label).toContain('UTC');
    expect(parts.utcTime).toBe('20:23');
    expect(parts.localTime).toMatch(/^\d{2}:\d{2}$/);
    expect(parts.localZone.length).toBeGreaterThan(0);
    // Local marker: abbrev (EST) or parenthetical offset
    expect(parts.label.includes(parts.localZone) || parts.label.includes('(')).toBe(
      true,
    );
  });

  it('formats the same instant in UTC zone as local=UTC', () => {
    const fixed = new Date('2026-11-13T15:23:00.000Z');
    const parts = formatLiveDecodeCurrentTime(fixed, 'UTC');
    expect(parts.utcTime).toBe('15:23');
    expect(parts.localTime).toBe('15:23');
    expect(parts.label).toContain('UTC');
  });

  it('falls back safely when Intl.DateTimeFormat throws (failure)', () => {
    const original = Intl.DateTimeFormat;
    const boom = vi.fn(() => {
      throw new RangeError('Invalid time zone');
    }) as unknown as typeof Intl.DateTimeFormat;
    // Keep constructor shape for `typeof Intl.DateTimeFormat === 'function'`
    Object.assign(boom, { supportedLocalesOf: original.supportedLocalesOf });
    vi.stubGlobal('Intl', { ...Intl, DateTimeFormat: boom });

    const fixed = new Date('2026-11-13T20:23:45.000Z');
    const parts = formatLiveDecodeCurrentTime(fixed);
    expect(parts.label).toMatch(/^Now: /);
    expect(parts.label).toContain('UTC');
    expect(parts.utcTime).toBe('20:23');
    expect(parts.localZone).toMatch(/UTC[+-]/);

    vi.unstubAllGlobals();
  });

  it('falls back when Intl is missing (failure)', () => {
    const saved = globalThis.Intl;
    // @ts-expect-error deliberate removal for fault path
    delete globalThis.Intl;
    const fixed = new Date('2026-11-13T08:05:00.000Z');
    const parts = formatLiveDecodeCurrentTime(fixed);
    expect(parts.label).toContain('UTC');
    expect(parts.utcTime).toBe('08:05');
    globalThis.Intl = saved;
  });
});

describe('live decode current-time prefs', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('defaults ON when unset (read happy path)', () => {
    expect(readShowLiveDecodeCurrentTime()).toBe(true);
  });

  it('persists OFF and ON (update mutation)', () => {
    writeShowLiveDecodeCurrentTime(false);
    expect(localStorage.getItem(LIVE_DECODE_SHOW_CURRENT_TIME_KEY)).toBe('false');
    expect(readShowLiveDecodeCurrentTime()).toBe(false);
    writeShowLiveDecodeCurrentTime(true);
    expect(readShowLiveDecodeCurrentTime()).toBe(true);
  });

  it('treats unknown stored values as ON (validation tolerance)', () => {
    localStorage.setItem(LIVE_DECODE_SHOW_CURRENT_TIME_KEY, 'maybe');
    expect(readShowLiveDecodeCurrentTime()).toBe(true);
  });

  it('survives localStorage getItem throw (failure)', () => {
    const spy = vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('blocked');
    });
    expect(readShowLiveDecodeCurrentTime()).toBe(true);
    spy.mockRestore();
  });

  it('survives localStorage setItem throw (failure)', () => {
    const spy = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('quota');
    });
    expect(() => writeShowLiveDecodeCurrentTime(false)).not.toThrow();
    spy.mockRestore();
  });
});
