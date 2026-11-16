/** Pure helpers for FileConverter conversion-status banner copy. */

export type ConversionStatusKind =
  | 'idle'
  | 'loading'
  | 'timeout'
  | 'error'
  | 'send_error';

/**
 * conversionStatusTitle.
 * @example
 * conversionStatusTitle('loading');
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
 * conversionStatusHasMessage('x');
 */
export function conversionStatusHasMessage(message: string | undefined): boolean {
  return Boolean(message);
}
