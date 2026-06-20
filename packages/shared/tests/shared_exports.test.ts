import { describe, expect, it } from 'vitest';
import {
  METAR_CORS_ORIGINS_ENV,
  VITE_API_BASE_URL_ENV,
  parseCommaSeparatedOrigins,
} from '../src/index';

describe('@metar/shared exports', () => {
  it('documents shared env variable names', () => {
    expect(METAR_CORS_ORIGINS_ENV).toBe('METAR_CORS_ORIGINS');
    expect(VITE_API_BASE_URL_ENV).toBe('VITE_API_BASE_URL');
  });

  it('parses comma-separated origins', () => {
    expect(parseCommaSeparatedOrigins('https://a.test, https://b.test')).toEqual([
      'https://a.test',
      'https://b.test',
    ]);
  });
});
