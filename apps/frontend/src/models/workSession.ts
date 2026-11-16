/**
 * Work-session payload shapes owned by the frontend.
 */

import type { StoredConverterPreferences } from './fileConverter';

/**
 * One conversion log issue row persisted on a work session.
 * @example
 * const _ = true;
 */
export interface WorkSessionLogIssue {
  code?: string;
  message?: string;
  severity?: string;
  level?: string;
  [key: string]: unknown;
}

/**
 * Conversion log blob on a work session.
 * @example
 * const _ = true;
 */
export interface WorkSessionConversionLog {
  errors: string[];
  issues: WorkSessionLogIssue[];
}

/**
 * Conversion params bag stored on a work session (superset of converter prefs).
 * @example
 * const _ = true;
 */
export type WorkSessionConversionParams = StoredConverterPreferences & {
  [key: string]: unknown;
};

/**
 * Convert API result fragment stored on a work session.
 * @example
 * const _ = true;
 */
export interface WorkSessionConvertResult {
  content?: string;
  iwxxm_xml?: string;
  xml?: string;
  tac_input?: string | null;
  ok?: boolean;
  [key: string]: unknown;
}
