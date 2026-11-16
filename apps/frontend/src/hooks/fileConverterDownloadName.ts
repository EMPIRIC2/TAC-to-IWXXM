/** Download filename helpers for converted FileConverter queue rows. */
import { manualDownloadXmlName, toIwxxmDownloadName } from '../utils/outputFilename';

/**
 * Type `LiveOutputSlot`.
 * @example
 * const _ = true;
 */
export type LiveOutputSlot = {
  index: number;
  total: number;
};

/**
 * Type `DownloadNameFile`.
 * @example
 * const _ = true;
 */
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
