import { describe, expect, it } from 'vitest';
import {
  conversionStatusHasMessage,
  conversionStatusTitle,
} from './fileConverterStatusUi';

describe('fileConverterStatusUi', () => {
  it('maps each status kind to a title', () => {
    expect(conversionStatusTitle('loading')).toBe('Converting...');
    expect(conversionStatusTitle('timeout')).toBe('Conversion Timeout');
    expect(conversionStatusTitle('send_error')).toBe('Send Error');
    expect(conversionStatusTitle('error')).toBe('Conversion Error');
    expect(conversionStatusTitle('idle')).toBe('Conversion Error');
  });

  it('detects optional status messages', () => {
    expect(conversionStatusHasMessage(undefined)).toBe(false);
    expect(conversionStatusHasMessage('')).toBe(false);
    expect(conversionStatusHasMessage('oops')).toBe(true);
  });
});
