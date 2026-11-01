/**
 * Unit tests for Strict raise helpers (ADR-054).
 */
import { describe, expect, it } from 'vitest';
import {
  isSeverityRaised,
  raisedSeveritySet,
  severityBlocksDownload,
} from './strictRaise';

describe('strictRaise', () => {
  it('Strict OFF raises only critical and error', () => {
    const set = raisedSeveritySet(false);
    expect(set.has('critical')).toBe(true);
    expect(set.has('error')).toBe(true);
    expect(set.has('warning')).toBe(false);
    expect(set.has('info')).toBe(false);
    expect(isSeverityRaised('warning', false)).toBe(false);
    expect(isSeverityRaised('error', false)).toBe(true);
  });

  it('Strict ON raises the full ladder', () => {
    expect(isSeverityRaised('info', true)).toBe(true);
    expect(isSeverityRaised('warning', true)).toBe(true);
  });

  it('only critical blocks download', () => {
    expect(severityBlocksDownload('critical')).toBe(true);
    expect(severityBlocksDownload('error')).toBe(false);
    expect(severityBlocksDownload('warning')).toBe(false);
  });
});
