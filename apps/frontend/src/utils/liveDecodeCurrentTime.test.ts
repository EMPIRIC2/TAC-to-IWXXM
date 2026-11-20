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
    class BoomDTF {
      static supportedLocalesOf = original.supportedLocalesOf.bind(original);
      constructor() {
        throw new RangeError('Invalid time zone');
      }
    }
    vi.stubGlobal('Intl', { ...Intl, DateTimeFormat: BoomDTF });

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

  it('falls back when local formatToParts omit hour/minute', () => {
    const original = Intl.DateTimeFormat;
    class StubDTF {
      static supportedLocalesOf = original.supportedLocalesOf.bind(original);
      formatToParts(): Intl.DateTimeFormatPart[] {
        return [{ type: 'literal', value: 'x' }];
      }
    }
    vi.stubGlobal('Intl', { ...Intl, DateTimeFormat: StubDTF });

    const fixed = new Date('2026-11-13T12:34:00.000Z');
    const parts = formatLiveDecodeCurrentTime(fixed);
    expect(parts.utcTime).toBe('12:34');
    expect(parts.label).toContain('UTC');
    vi.unstubAllGlobals();
  });

  it('uses shortOffset / fallback when short zone name is blank', () => {
    const original = Intl.DateTimeFormat;
    class StubDTF {
      static supportedLocalesOf = original.supportedLocalesOf.bind(original);
      private readonly opts: { timeZoneName?: string; timeZone?: string };
      constructor(
        _locales?: unknown,
        opts?: { timeZoneName?: string; timeZone?: string },
      ) {
        this.opts = opts ?? {};
      }
      formatToParts(date: Date): Intl.DateTimeFormatPart[] {
        const tzName = this.opts.timeZoneName;
        if (tzName === 'short') {
          return [
            { type: 'hour', value: '09' },
            { type: 'literal', value: ':' },
            { type: 'minute', value: '01' },
            { type: 'timeZoneName', value: '   ' },
          ];
        }
        if (tzName === 'shortOffset') {
          return [{ type: 'timeZoneName', value: 'GMT-5' }];
        }
        if (this.opts.timeZone === 'UTC') {
          return [
            { type: 'hour', value: String(date.getUTCHours()).padStart(2, '0') },
            { type: 'minute', value: String(date.getUTCMinutes()).padStart(2, '0') },
          ];
        }
        return [];
      }
    }
    vi.stubGlobal('Intl', { ...Intl, DateTimeFormat: StubDTF });

    const fixed = new Date('2026-11-13T14:01:00.000Z');
    const parts = formatLiveDecodeCurrentTime(fixed, 'America/New_York');
    expect(parts.localTime).toBe('09:01');
    expect(parts.localZone).toBe('GMT-5');
    expect(parts.label).toContain('(GMT-5)');
    vi.unstubAllGlobals();
  });

  it('uses offset fallback zone when short and shortOffset names are empty', () => {
    const original = Intl.DateTimeFormat;
    class StubDTF {
      static supportedLocalesOf = original.supportedLocalesOf.bind(original);
      private readonly opts: { timeZoneName?: string; timeZone?: string };
      constructor(
        _locales?: unknown,
        opts?: { timeZoneName?: string; timeZone?: string },
      ) {
        this.opts = opts ?? {};
      }
      formatToParts(date: Date): Intl.DateTimeFormatPart[] {
        if (
          this.opts.timeZoneName === 'short' ||
          this.opts.timeZoneName === 'shortOffset'
        ) {
          return [
            { type: 'hour', value: '10' },
            { type: 'minute', value: '00' },
            { type: 'timeZoneName', value: '' },
          ];
        }
        if (this.opts.timeZone === 'UTC') {
          return [
            { type: 'hour', value: String(date.getUTCHours()).padStart(2, '0') },
            { type: 'minute', value: String(date.getUTCMinutes()).padStart(2, '0') },
          ];
        }
        return [
          { type: 'hour', value: '10' },
          { type: 'minute', value: '00' },
        ];
      }
    }
    vi.stubGlobal('Intl', { ...Intl, DateTimeFormat: StubDTF });

    const fixed = new Date('2026-11-13T15:00:00.000Z');
    const parts = formatLiveDecodeCurrentTime(fixed);
    expect(parts.localTime).toBe('10:00');
    expect(parts.localZone).toMatch(/UTC[+-]/);
    expect(parts.label).toContain('(');
    vi.unstubAllGlobals();
  });

  it('falls back when UTC formatToParts omit hour/minute', () => {
    const original = Intl.DateTimeFormat;
    class StubDTF {
      static supportedLocalesOf = original.supportedLocalesOf.bind(original);
      private readonly opts: { timeZone?: string };
      constructor(_locales?: unknown, opts?: { timeZone?: string }) {
        this.opts = opts ?? {};
      }
      formatToParts(): Intl.DateTimeFormatPart[] {
        if (this.opts.timeZone === 'UTC') {
          return [{ type: 'literal', value: 'x' }];
        }
        return [
          { type: 'hour', value: '11' },
          { type: 'minute', value: '22' },
          { type: 'timeZoneName', value: 'EST' },
        ];
      }
    }
    vi.stubGlobal('Intl', { ...Intl, DateTimeFormat: StubDTF });

    const fixed = new Date('2026-11-13T16:22:00.000Z');
    const parts = formatLiveDecodeCurrentTime(fixed);
    expect(parts.utcTime).toBe('16:22');
    expect(parts.label).toContain('UTC');
    vi.unstubAllGlobals();
  });

  it('formats fallback with negative local offset (west of UTC)', () => {
    const saved = globalThis.Intl;
    // @ts-expect-error deliberate removal for fallback path
    delete globalThis.Intl;
    const fixed = new Date('2026-11-13T18:00:00.000Z');
    vi.spyOn(fixed, 'getTimezoneOffset').mockReturnValue(300); // UTC-5
    vi.spyOn(fixed, 'getHours').mockReturnValue(13);
    vi.spyOn(fixed, 'getMinutes').mockReturnValue(0);
    const parts = formatLiveDecodeCurrentTime(fixed);
    expect(parts.localZone).toBe('UTC-05:00');
    expect(parts.label).toContain('(UTC-05:00)');
    globalThis.Intl = saved;
    vi.restoreAllMocks();
  });

  it('formats fallback with positive local offset (east of UTC)', () => {
    const saved = globalThis.Intl;
    // @ts-expect-error deliberate removal for fallback path
    delete globalThis.Intl;
    const fixed = new Date('2026-11-13T18:00:00.000Z');
    vi.spyOn(fixed, 'getTimezoneOffset').mockReturnValue(-120); // UTC+2
    vi.spyOn(fixed, 'getHours').mockReturnValue(20);
    vi.spyOn(fixed, 'getMinutes').mockReturnValue(0);
    const parts = formatLiveDecodeCurrentTime(fixed);
    expect(parts.localZone).toBe('UTC+02:00');
    expect(parts.label).toContain('(UTC+02:00)');
    globalThis.Intl = saved;
    vi.restoreAllMocks();
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
