import type { ConversionIssue } from './openapi';
/** FileConverter workbench models. */

import type { WorkSession } from '@metar/shared';
import type { TacProductSelection } from '@/utils/tacProduct';
import type { IwxxmProfile } from '@/utils/tacProduct';
import type { ExchangeProfileId } from '@/utils/exchangeProfile';
import type { ConversionExportContext } from '@/utils/conversionExportMetadata';
import type { IwxxmVersionId } from '@/utils/iwxxmVersions';
import type { ResultIssueInput } from '@/utils/resultCard';

/**
 * Issues captured for one converted result card.
 * @example
 * const _ = true;
 */
export interface ConvertedFileResultCard {
  errors: string[];
  issues: ResultIssueInput[];
  ok?: boolean;
}

/**
 * Type `ConvertedFile`.
 * @example
 * const _ = true;
 */
export interface ConvertedFile {
  id: string;
  originalName: string;
  originalContent: string;
  convertedContent: string;
  timestamp: number;
  /** TAC-derived card title (e.g. METAR KJFK 121251Z). */
  displayTitle: string;
  /** 1-based index when manual input had multiple lines. */
  manualLineIndex?: number;
  manualLineTotal?: number;
  /**
   * When set, Download / ZIP member names follow the live Output filename
   * field (#904) instead of convert-time {@link originalName}.
   * `index` is 0-based; `total` is the manual batch size.
   */
  liveOutputSlot?: { index: number; total: number };
  /** Convert-time snapshot for export metadata sidecars. */
  exportContext?: ConversionExportContext;
  /** Issues captured for this result. Older saved cards omit it. */
  resultCard?: ConvertedFileResultCard;
}

/**
 * Type `PendingFile`.
 * @example
 * const _ = true;
 */
export interface PendingFile {
  id: string;
  name: string;
  content: string;
}

/**
 * Type `FileConverterProps`.
 * @example
 * const _ = true;
 */
export interface FileConverterProps {
  /** JWT for server session APIs when logged in (F31). Convert stays public. */
  accessToken?: string;
  /** Display name in preferences / header context. */
  userEmail?: string;
  /** True when operating without Auth (guest IndexedDB path). */
  isGuest?: boolean;
  /** Logout / return to guest after scoped sign-out. */
  onLogout?: () => void;
  /** Open optional login UX (F31 / F21 Amended). */
  onRequestLogin?: () => void;
  onOpenHistory?: () => void;
  /** Open full-page Live map (live TAC map). */
  onOpenVisuals?: () => void;
  onLoadWorkSession?: (session: WorkSession) => void;
  onNewMetar?: () => void;
  onSessionUpdated?: (session: WorkSession) => void;
  onActiveSessionIdChange?: (id: string | null) => void;
  activeWorkSessionId?: string | null;
  loadedWorkSession?: WorkSession | null;
  /** TAC from Live map Send — applied once then cleared. */
  pendingMapTac?: string | null;
  /** Clear pending map TAC after it is applied to the editor. */
  onPendingMapTacConsumed?: () => void;
  /** Open Rule catalogs (optional family hint for Convert trust links). */
  onOpenCatalog?: (
    family?: 'conversion' | 'lint' | 'iwxxm' | 'decoding',
    code?: string,
  ) => void;
}

/**
 * Type `ConversionParams`.
 * @example
 * const _ = true;
 */
export interface ConversionParams {
  bulletinId: string;
  issuingCenter: string;
  product: TacProductSelection;
  profile: IwxxmProfile;
  reportVariant: string;
  exchangeProfile: ExchangeProfileId;
  /** Optional saved semantic preset UUID (empty = none). */
  presetId: string;
  /** Optional saved dissemination template UUID (empty = none). */
  disseminationTemplateId: string;
  /** Optional signed ConversionProfile overlay UUID (empty = none). */
  overlayId: string;
  conversionLibraryId: string;
  tacValidationLibraryId: string;
  iwxxmValidationLibraryId: string;
  disseminationLibraryId: string;
  decodingLibraryId: string;
  iwxxmVersion: IWXXMVersion;
  strictValidation: boolean;
  strictLint: boolean;
  strictConvert: boolean;
  strictValidate: boolean;
  includeNilReasons: boolean;
  onError: OnErrorBehavior;
  logLevel: LogLevel;
}

/**
 * Type `IWXXMVersion`.
 * @example
 * const _ = true;
 */
export type IWXXMVersion = IwxxmVersionId;

/**
 * Type `OnErrorBehavior`.
 * @example
 * const _ = true;
 */
export type OnErrorBehavior = 'skip' | 'fail' | 'warn';

/**
 * Type `LogLevel`.
 * @example
 * const _ = true;
 */
export type LogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';

/**
 * Converter preferences blob read from storage / preference center.
 * @example
 * const _ = true;
 */
export interface StoredConverterPreferences {
  bulletinIdExample?: string;
  issuingCenter?: string;
  product?: string;
  profile?: unknown;
  exchangeProfile?: unknown;
  iwxxmVersion?: unknown;
  strictValidation?: boolean;
  strictLint?: boolean;
  strictConvert?: boolean;
  strictValidate?: boolean;
  includeNilReasons?: boolean;
  onError?: string;
  logLevel?: string;
  [key: string]: unknown;
}

/**
 * Operator-facing conversion log panel payload.
 * @example
 * const _ = true;
 */
export interface ConversionLog {
  errors: string[];
  issues: ConversionIssue[];
}
