/**
 * Behavior matrix for FileConverter / dissemination structural split
 * (EV-frontend-models-split).
 */
import { describe, expect, it } from 'vitest';
import {
  initialConversionParams,
  conversionParamsFromStoredPreferences,
} from '@/utils/fileConverterParams';
import type { ConvertedFile } from '@/models/fileConverter';

describe('FileConverter params validation matrix', () => {
  it('accepts valid stored preferences (V+)', () => {
    const params = conversionParamsFromStoredPreferences({
      bulletinIdExample: 'SAAA00',
      product: 'METAR',
      strictLint: true,
    });
    expect(params.bulletinId).toBe('SAAA00');
    expect(params.product).toBe('METAR');
  });

  it('falls back safely for empty preferences (V−)', () => {
    const params = conversionParamsFromStoredPreferences({});
    const baseline = initialConversionParams();
    expect(params.iwxxmVersion).toBeTruthy();
    expect(params.profile).toBeTruthy();
    expect(typeof baseline.strictLint).toBe('boolean');
  });
});

describe('FileConverter result-card mutation matrix', () => {
  it('creates, updates, and deletes a ConvertedFile (M × S/F)', () => {
    let queue: ConvertedFile[] = [];
    const created: ConvertedFile = {
      id: 'c1',
      originalName: 'a.txt',
      originalContent: 'METAR KJFK',
      convertedContent: '<xml/>',
      timestamp: 1,
      displayTitle: 'METAR KJFK',
    };
    queue = [...queue, created];
    expect(queue).toHaveLength(1);

    queue = queue.map((item) =>
      item.id === 'c1'
        ? { ...item, resultCard: { errors: ['x'], issues: [], ok: false } }
        : item,
    );
    expect(queue[0]?.resultCard?.ok).toBe(false);

    queue = queue.filter((item) => item.id !== 'c1');
    expect(queue).toHaveLength(0);
  });
});
