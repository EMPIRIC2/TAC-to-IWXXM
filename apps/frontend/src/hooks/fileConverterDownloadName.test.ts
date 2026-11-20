import { describe, expect, it } from 'vitest';
import { resolveConvertedDownloadXmlName } from './fileConverterDownloadName';

describe('resolveConvertedDownloadXmlName', () => {
  it('uses live output slot naming when present', () => {
    expect(
      resolveConvertedDownloadXmlName(
        { liveOutputSlot: { index: 2, total: 5 }, originalName: 'ignored.metar' },
        'bulletin.xml',
      ),
    ).toMatch(/bulletin/i);
  });

  it('falls back to original name and empty original', () => {
    expect(
      resolveConvertedDownloadXmlName({ originalName: 'report.metar' }, 'x.xml'),
    ).toMatch(/\.xml$/);
    expect(resolveConvertedDownloadXmlName({}, 'x.xml')).toBe('download.xml');
    expect(resolveConvertedDownloadXmlName({ originalName: null }, 'x.xml')).toBe(
      'download.xml',
    );
  });
});
