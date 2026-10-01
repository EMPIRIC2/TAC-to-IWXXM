import { describe, expect, it } from 'vitest';
import {
  catalogEntryMatchesQuery,
  catalogFamilyLabel,
  selectedCatalogCode,
} from './catalogPresentation';

describe('catalogPresentation', () => {
  it('names each catalog family', () => {
    expect(catalogFamilyLabel('lint')).toBe('TAC validation');
    expect(catalogFamilyLabel('iwxxm')).toBe('IWXXM validation');
    expect(catalogFamilyLabel('conversion')).toBe('Conversion');
    expect(catalogFamilyLabel('dissemination')).toBe('Dissemination');
    expect(catalogFamilyLabel('decoding')).toBe('Decoding');
    expect(catalogFamilyLabel('  ')).toBe('—');
    expect(catalogFamilyLabel(null)).toBe('—');
    expect(catalogFamilyLabel('custom')).toBe('custom');
  });

  it('matches a search against the code and the description', () => {
    expect(catalogEntryMatchesQuery('EMPTY_TAC', 'TAC is empty', '   ')).toBe(true);
    expect(catalogEntryMatchesQuery('EMPTY_TAC', 'TAC is empty', 'empty')).toBe(true);
    expect(catalogEntryMatchesQuery('EMPTY_TAC', 'TAC is empty', 'wind')).toBe(false);
    expect(catalogEntryMatchesQuery(null, null, 'x')).toBe(false);
  });

  it('keeps the selected code when it is still in the list', () => {
    expect(selectedCatalogCode([], 'A')).toBeNull();
    expect(selectedCatalogCode(['A', 'B'], null)).toBe('A');
    expect(selectedCatalogCode(['A', 'B'], 'B')).toBe('B');
    expect(selectedCatalogCode(['A', 'B'], 'Z')).toBe('A');
  });
});
