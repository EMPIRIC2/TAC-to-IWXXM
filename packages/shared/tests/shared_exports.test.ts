import { describe, expect, it } from 'vitest';
import {
  METAR_CORS_ORIGINS_ENV,
  VITE_API_BASE_URL_ENV,
  VITE_APP_URL_ENV,
  VITE_SUPABASE_PUBLISHABLE_KEY_ENV,
  VITE_SUPABASE_URL_ENV,
  parseCommaSeparatedOrigins,
} from '../src/index';

describe('@metar/shared exports', () => {
  it('documents shared env variable names', () => {
    expect(METAR_CORS_ORIGINS_ENV).toBe('METAR_CORS_ORIGINS');
    expect(VITE_API_BASE_URL_ENV).toBe('VITE_API_BASE_URL');
    expect(VITE_SUPABASE_URL_ENV).toBe('VITE_SUPABASE_URL');
    expect(VITE_SUPABASE_PUBLISHABLE_KEY_ENV).toBe(
      'VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY',
    );
    expect(VITE_APP_URL_ENV).toBe('VITE_APP_URL');
  });

  it('parses comma-separated origins', () => {
    expect(parseCommaSeparatedOrigins('https://a.test, https://b.test')).toEqual([
      'https://a.test',
      'https://b.test',
    ]);
  });

  it('returns empty list for undefined, blank, or whitespace-only input', () => {
    expect(parseCommaSeparatedOrigins(undefined)).toEqual([]);
    expect(parseCommaSeparatedOrigins('')).toEqual([]);
    expect(parseCommaSeparatedOrigins('   ')).toEqual([]);
  });

  it('filters empty segments and trims each origin', () => {
    expect(parseCommaSeparatedOrigins('https://a.test,, https://b.test , ,')).toEqual([
      'https://a.test',
      'https://b.test',
    ]);
  });
});
