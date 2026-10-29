/**
 * Shared operator emphasis for error vs note/warning severity rows.
 *
 * Used by TAC notes jumps and conversion/validation log cards so destructive
 * styling is not one-list-only. [Corpus: ui-style]
 */

import { isErrorSeverity } from '@/utils/resultCard';

/**
 * Default jump / list row chrome (notes and warnings).
 *
 * @returns Tailwind class string
 * @example
 * const _ = true;
 */
export function lintSeverityBaseClass(): string {
  return 'rounded px-2 py-0.5 text-left text-xs text-gray-900 dark:text-gray-100';
}

/**
 * Error emphasis: destructive text, semibold, light tint (not colour alone —
 * callers still show a severity label).
 *
 * @returns Tailwind class string
 * @example
 * const _ = true;
 */
export function lintSeverityErrorClass(): string {
  return 'rounded px-2 py-0.5 text-left text-xs font-semibold text-destructive bg-destructive/10 dark:bg-destructive/20';
}

/**
 * Card shell tint for error issues inside Conversion / validation log.
 *
 * @returns Tailwind class string
 * @example
 * const _ = true;
 */
export function lintSeverityErrorCardClass(): string {
  return 'rounded border border-destructive/40 bg-destructive/10 p-2 dark:border-destructive/50 dark:bg-destructive/20';
}

/**
 * Tailwind classes for a TAC notes jump button by severity.
 *
 * @param severity - Engine severity token
 * @returns Class string (error uses destructive tokens)
 * @example
 * const _ = true;
 */
export function lintJumpButtonClass(severity: string | null | undefined): string {
  return isErrorSeverity(severity) ? lintSeverityErrorClass() : lintSeverityBaseClass();
}

/**
 * Whether an issue card should use destructive emphasis (errors section).
 *
 * @param severity - Engine severity token
 * @returns True for publish-blocking / error ranks
 * @example
 * const _ = true;
 */
export function isErrorSeverityEmphasis(severity: string | null | undefined): boolean {
  return isErrorSeverity(severity);
}
