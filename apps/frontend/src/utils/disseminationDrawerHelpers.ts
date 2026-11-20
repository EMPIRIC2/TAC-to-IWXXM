/* eslint-disable complexity */
/**
 * Pure helpers extracted from DisseminationDrawer.
 */
import { convertMetarToIwxxm } from '/utils/api';
import { resolveDisseminationProduct } from '@/utils/fileInputHelpers';
import type { ExportCandidate } from '@/utils/exportSelection';
import type { ExchangeProfileId } from '@/utils/exchangeProfile';

export { resolveDisseminationProduct } from '@/utils/fileInputHelpers';
export {
  hasDropFiles,
  dropReaderText,
  progressRowState,
} from '@/utils/disseminationDrawerPure';

/**
 * Resolve IWXXM XML for a candidate, converting TAC when needed.
 *
 * @param candidate - Export row (session or drop)
 * @param product - Default product tag
 * @param exchangeProfile - Exchange overlay wire id for convert FormData
 * @returns IWXXM XML string
 * @throws When convert fails or returns no XML
 * @example
 * const _ = true;
 */
/**
 * resolveCandidateIwxxmXml.
 * @example
 * const _ = true;
 */
export async function resolveCandidateIwxxmXml(
  candidate: ExportCandidate,
  product: string,
  exchangeProfile: ExchangeProfileId,
): Promise<string> {
  const existing = candidate.iwxxmXml?.trim();
  if (existing) return existing;
  const tac = candidate.tacText?.trim();
  if (!tac) {
    throw new Error('Candidate has neither IWXXM XML nor TAC text');
  }
  const response = await convertMetarToIwxxm({
    manualText: tac,
    product: resolveDisseminationProduct(candidate.product, product).toUpperCase(),
    exchangeProfile,
  });
  const xml =
    response.results?.[0]?.iwxxm_xml?.trim() ||
    (response.results?.[0] as { xml?: string } | undefined)?.xml?.trim() ||
    (response.results?.[0] as { content?: string } | undefined)?.content?.trim() ||
    '';
  if (!xml) {
    throw new Error('Convert returned no IWXXM XML for dissemination');
  }
  return xml;
}
