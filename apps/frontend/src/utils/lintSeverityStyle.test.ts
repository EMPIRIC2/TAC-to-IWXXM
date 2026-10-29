/**
 * Shared error vs note severity chrome for TAC notes and conversion log.
 */
import { describe, expect, it } from 'vitest';
import {
  isErrorSeverityEmphasis,
  lintJumpButtonClass,
  lintSeverityBaseClass,
  lintSeverityErrorCardClass,
  lintSeverityErrorClass,
} from './lintSeverityStyle';

describe('lintSeverityStyle', () => {
  it('uses destructive jump chrome for error and missing severity', () => {
    for (const severity of [
      'error',
      'ERROR',
      'critical',
      '',
      null,
      undefined,
    ] as const) {
      const cls = lintJumpButtonClass(severity);
      expect(cls).toContain('text-destructive');
      expect(cls).toContain('font-semibold');
      expect(cls).toMatch(/bg-destructive\//);
      expect(cls).toContain('rounded');
      expect(cls.length).toBeGreaterThan(20);
    }
    expect(lintSeverityErrorClass()).toContain('text-destructive');
    expect(lintSeverityErrorClass()).toContain('font-semibold');
    expect(lintSeverityErrorClass()).toMatch(/bg-destructive\//);
  });

  it('keeps note and warning jumps on the base chrome', () => {
    for (const severity of ['warning', 'warn', 'info', 'note'] as const) {
      const cls = lintJumpButtonClass(severity);
      expect(cls).not.toContain('text-destructive');
      expect(cls).not.toMatch(/bg-destructive\//);
      expect(cls).toContain('text-gray-900');
      expect(cls).toContain('dark:text-gray-100');
      expect(cls.length).toBeGreaterThan(20);
    }
    expect(lintSeverityBaseClass()).toContain('text-gray-900');
    expect(lintSeverityBaseClass()).not.toContain('text-destructive');
  });

  it('flags error card emphasis with the shared destructive card class', () => {
    expect(isErrorSeverityEmphasis('error')).toBe(true);
    expect(isErrorSeverityEmphasis('critical')).toBe(true);
    expect(isErrorSeverityEmphasis('')).toBe(true);
    expect(isErrorSeverityEmphasis('warning')).toBe(false);
    expect(isErrorSeverityEmphasis('info')).toBe(false);
    const card = lintSeverityErrorCardClass();
    expect(card).toMatch(/border-destructive/);
    expect(card).toMatch(/bg-destructive\//);
    expect(card).toContain('p-2');
    expect(card.length).toBeGreaterThan(20);
  });
});
