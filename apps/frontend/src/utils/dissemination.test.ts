/**
 * Unit tests for dissemination client helpers (T6.1 / F16–F19).
 */

import { describe, expect, it } from 'vitest';

import {
  DRAWER_SINK_TYPES,
  DB_SINK_TYPES,
  isPreflightGreen,
  sinkTypeLabel,
} from './dissemination';

describe('dissemination helpers', () => {
  it('exports drawer sink types aligned with backend DRAWER_SINK_TYPES', () => {
    expect([...DRAWER_SINK_TYPES]).toEqual([
      'postgres',
      'mysql',
      'sqlserver',
      'sqlite',
      'wis2',
      'edis',
      'amhs',
      'swim',
      'afs',
    ]);
    for (const db of DB_SINK_TYPES) {
      expect(DRAWER_SINK_TYPES).toContain(db);
    }
  });

  it('labels sinks for the chooser', () => {
    expect(sinkTypeLabel('postgres')).toMatch(/postgres/i);
    expect(sinkTypeLabel('mysql')).toMatch(/mysql/i);
    expect(sinkTypeLabel('amhs')).toBe('AMHS');
  });

  it('gates Send on green preflight only', () => {
    expect(isPreflightGreen(undefined)).toBe(false);
    expect(
      isPreflightGreen({
        ok: true,
        connectivity_ok: true,
        diffs: [],
        handle: 'h',
      }),
    ).toBe(true);
  });
});
