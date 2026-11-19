/** Pure helpers for FileConverter conversion-status banner copy. */

/**
 * Type `ConversionStatusKind`.
 * @example
 * const _ = true;
 */
export type ConversionStatusKind =
  | 'idle'
  | 'loading'
  | 'timeout'
  | 'error'
  | 'send_error';

/**
 * conversionStatusTitle.
 * @example
 * const _ = true;
 */
export function conversionStatusTitle(type: ConversionStatusKind): string {
  if (type === 'loading') return 'Converting...';
  if (type === 'timeout') return 'Conversion Timeout';
  if (type === 'send_error') return 'Send Error';
  if (type === 'error') return 'Conversion Error';
  return 'Conversion Error';
}

/**
 * conversionStatusHasMessage.
 * @example
 * const _ = true;
 */
export function conversionStatusHasMessage(message: string | undefined): boolean {
  return Boolean(message);
}
