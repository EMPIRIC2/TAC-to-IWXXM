/** Dissemination drawer props and BYOC param bag. */

import type { ExportCandidateInput } from '@/utils/exportSelection';
import type { ExchangeProfileId } from '@/utils/exchangeProfile';

/**
 * Type `DisseminationDrawerProps`.
 * @example
 * const _ = true;
 */
export interface DisseminationDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Converted IWXXM XML (convert-then-send path). */
  iwxxmXml?: string;
  /** Optional TAC text for drag-drop / convert paths. */
  tacText?: string;
  product?: string;
  /** Extra current-session outputs (beyond primary convert props). */
  sessionOutputs?: ExportCandidateInput[];
  accessToken?: string;
  disseminationTemplateId?: string;
  onDisseminationTemplateChange?: (templateId: string) => void;
  /**
   * Initial exchange overlay (workbench). Drawer keeps local state after open so
   * packaging can override without mutating convert params; optional callback
   * notifies the parent (e.g. Validation Issues Catalog filter) of the active
   * packaging Exchange.
   */
  exchangeProfile?: ExchangeProfileId | string;
  /** Fired when the packaging Exchange control changes (and once on mount). */
  onExchangeProfileChange?: (profile: ExchangeProfileId) => void;
}

/**
 * Parsed BYOC destination params (memory-only).
 * @example
 * const _ = true;
 */
export interface ByocDestinationParams {
  [key: string]: unknown;
}

/**
 * Progress row UI state for one dissemination candidate.
 * @example
 * const _ = true;
 */
export interface DisseminationRowUiState {
  status: 'pending' | 'running' | 'ok' | 'error' | string;
  error?: string;
  [key: string]: unknown;
}
