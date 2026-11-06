import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  CATALOG_VIEW_STORAGE_KEY,
  parseCatalogView,
  readCatalogView,
  writeCatalogView,
} from './catalogView';

describe('catalogView', () => {
  afterEach(() => {
    sessionStorage.removeItem(CATALOG_VIEW_STORAGE_KEY);
    vi.unstubAllGlobals();
  });

  it('treats unknown values as detailed and stores a compact choice', () => {
    expect(parseCatalogView(null)).toBe('detailed');
    expect(parseCatalogView(undefined)).toBe('detailed');
    expect(parseCatalogView('other')).toBe('detailed');
    expect(parseCatalogView('compact')).toBe('compact');
    expect(readCatalogView()).toBe('detailed');
    writeCatalogView('compact');
    expect(sessionStorage.getItem(CATALOG_VIEW_STORAGE_KEY)).toBe('compact');
    expect(readCatalogView()).toBe('compact');
  });

  it('keeps detailed when session storage is missing or throws', () => {
    vi.stubGlobal('window', {});
    expect(readCatalogView()).toBe('detailed');
    writeCatalogView('compact');

    const storage = {
      getItem: () => {
        throw new Error('blocked');
      },
      setItem: () => {
        throw new Error('blocked');
      },
    };
    vi.stubGlobal('window', { sessionStorage: storage });
    expect(readCatalogView()).toBe('detailed');
    writeCatalogView('compact');
  });
});
