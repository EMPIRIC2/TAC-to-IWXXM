/**
 * Omit blank strings from optional multipart / JSON fields.
 *
 * @param value - Raw form field
 * @returns Trimmed value, or undefined when empty
 * @example
 * const _ = true;
 */
export function optionalFormField(value: string | undefined): string | undefined {
  const trimmed = value?.trim() ?? '';
  return trimmed ? trimmed : undefined;
}
