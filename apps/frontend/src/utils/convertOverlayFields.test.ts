import { describe, expect, it } from 'vitest';
import { convertOverlayFields } from './convertOverlayFields';

describe('convertOverlayFields', () => {
  it('returns empty object when overlay id is blank', () => {
    expect(convertOverlayFields('')).toEqual({});
    expect(convertOverlayFields('   ', 'tok')).toEqual({});
  });

  it('returns overlay id alone when token is missing', () => {
    expect(convertOverlayFields('ov-1')).toEqual({ overlayId: 'ov-1' });
    expect(convertOverlayFields(' ov-1 ', '  ')).toEqual({ overlayId: 'ov-1' });
  });

  it('returns overlay id and token when both present', () => {
    expect(convertOverlayFields('ov-1', ' jwt ')).toEqual({
      overlayId: 'ov-1',
      accessToken: 'jwt',
    });
  });
});
