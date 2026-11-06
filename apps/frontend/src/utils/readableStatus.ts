/**
 * Written status labels for diffs and the validation catalog.
 */

/**
 * Word for a diff line, so added and removed lines are not colour alone.
 *
 * @param op - Diff operation
 * @returns Added, Removed, Same, or an empty string for a blank cell
 * @example
 * const _ = true;
 */
export function diffChangeLabel(op: string): string {
  if (op === 'add') return 'Added';
  if (op === 'remove') return 'Removed';
  if (op === 'empty') return '';
  return 'Same';
}

/**
 * Catalog level written out.
 *
 * @param severity - Engine severity, or blank when the row has none
 * @returns Error, Warning, Info, Critical, a capitalized token, or an em dash
 * @example
 * const _ = true;
 */
export function catalogLevelLabel(severity: string | null | undefined): string {
  const raw = (severity ?? '').trim();
  if (!raw) return '—';
  const key = raw.toLowerCase();
  if (key === 'error') return 'Error';
  if (key === 'warning' || key === 'warn') return 'Warning';
  if (key === 'info') return 'Info';
  if (key === 'critical') return 'Critical';
  return raw.charAt(0).toUpperCase() + raw.slice(1);
}
