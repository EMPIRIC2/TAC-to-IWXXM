/**
 * EV-080 M3 — pure-helper branch fills for remaining <100% modules.
 */
import { describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import {
  compareEntries,
  entryMatchesLevelFilter,
  sortFieldValue,
} from '@/app/components/LintValidationCatalogPage';
import { emailLocalPart } from '@/app/components/UserPreferencesDialog';
import { SystemSettingsPanel } from '@/app/components/admin/SystemSettingsPanel';
import type { LintIssueCatalogEntry } from '@/utils/openapiTypes';

const mockToast = vi.hoisted(() => ({
  error: vi.fn(),
  success: vi.fn(),
  info: vi.fn(),
}));

vi.mock('sonner', () => ({
  toast: mockToast,
}));

describe('EV-080 emailLocalPart', () => {
  it('returns local-part or empty when missing', () => {
    expect(emailLocalPart('ops@example.com')).toBe('ops');
    expect(emailLocalPart('@example.com')).toBe('');
  });
});

describe('EV-080 LintValidationCatalog sort helpers', () => {
  const base = {
    code: 'C1',
    severity: 'error',
    family: 'lint',
    issue_type: 'structure',
    source_access: 'public',
    description: 'd',
    message_template: 't',
    tags: [],
  } as unknown as LintIssueCatalogEntry;

  it('uses empty-string fallbacks for missing sortable fields', () => {
    const sparse = {
      code: undefined,
      severity: undefined,
      family: undefined,
      issue_type: undefined,
      source_access: undefined,
    } as unknown as LintIssueCatalogEntry;
    expect(sortFieldValue(sparse, 'family')).toBe('');
    expect(sortFieldValue(sparse, 'issue_type')).toBe('');
    expect(sortFieldValue(sparse, 'source_access')).toBe('');
    expect(sortFieldValue(sparse, 'code')).toBe('');
  });

  it('compares by level with missing severity falling back to rank 99', () => {
    const a = { ...base, severity: undefined as unknown as string, code: 'B' };
    const b = { ...base, severity: 'error', code: 'A' };
    expect(compareEntries(a, b, 'level')).toBeGreaterThan(0);
    expect(compareEntries(b, a, 'level')).toBeLessThan(0);
    expect(
      compareEntries(
        { ...base, severity: 'error', code: '' },
        { ...base, severity: 'error', code: undefined as unknown as string },
        'level',
      ),
    ).toBe(0);
  });

  it('uses code tie-break when primary sort keys match', () => {
    expect(
      compareEntries(
        { ...base, family: 'lint', code: 'A' },
        { ...base, family: 'lint', code: 'B' },
        'family',
      ),
    ).toBeLessThan(0);
    expect(
      compareEntries(
        { ...base, family: 'lint', code: '' },
        { ...base, family: 'lint', code: undefined as unknown as string },
        'family',
      ),
    ).toBe(0);
  });

  it('compares by family / issue_type / source_access', () => {
    expect(
      compareEntries({ ...base, family: 'a' }, { ...base, family: 'b' }, 'family'),
    ).toBeLessThan(0);
    expect(
      compareEntries(
        { ...base, issue_type: 'z' },
        { ...base, issue_type: 'a' },
        'issue_type',
      ),
    ).toBeGreaterThan(0);
    expect(
      compareEntries(
        { ...base, source_access: 'a' },
        { ...base, source_access: 'a' },
        'source_access',
      ),
    ).toBe(0);
  });

  it('matches level filter with missing severity via empty-string fallback', () => {
    expect(entryMatchesLevelFilter(base, null)).toBe(true);
    expect(entryMatchesLevelFilter(base, 'error')).toBe(true);
    expect(
      entryMatchesLevelFilter(
        { ...base, severity: undefined as unknown as string },
        'error',
      ),
    ).toBe(false);
    expect(entryMatchesLevelFilter({ ...base, severity: '' }, 'error')).toBe(false);
  });
});

describe('EV-080 SystemSettings reset without originals', () => {
  it('no-ops reset when load failed and originalSettings is null', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, json: async () => ({}) }),
    );
    const user = userEvent.setup();
    render(<SystemSettingsPanel accessToken="tok" />);
    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalled();
    });
    await user.click(screen.getByRole('button', { name: /reset/i }));
    expect(mockToast.info).not.toHaveBeenCalled();
  });
});
