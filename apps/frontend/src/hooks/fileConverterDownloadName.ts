/** Download filename helpers for converted FileConverter queue rows. */
import { manualDownloadXmlName, toIwxxmDownloadName } from '../utils/outputFilename';

export type LiveOutputSlot = {
  index: number;
  total: number;
};

export type DownloadNameFile = {
  originalName?: string | null;
  liveOutputSlot?: LiveOutputSlot | null;
};

/**
 * resolveConvertedDownloadXmlName.
 * @example
 * resolveConvertedDownloadXmlName({ originalName: 'a.metar' }, 'out.xml');
 */
export function resolveConvertedDownloadXmlName(
  file: DownloadNameFile,
  outputFilename: string,
): string {
  if (file.liveOutputSlot) {
    return manualDownloadXmlName(
      outputFilename,
      file.liveOutputSlot.index,
      file.liveOutputSlot.total,
    );
  }
  return toIwxxmDownloadName(file.originalName ?? '');
}
