/**
 * Progress for the live Convert screen. Labels describe state. They do not
 * block editing, preview, or validate.
 */

/**
 * Type `LiveConvertStatusStripProps`.
 * @example
 * const _ = true;
 */
export interface LiveConvertStatusStripProps {
  hasTac: boolean;
  decodeReady: boolean;
  decodeLoading: boolean;
  previewState: 'waiting' | 'current' | 'incomplete';
  lintStatus: 'waiting' | 'running' | 'passed' | 'failed' | 'warnings';
  schemaStatus: 'not run' | 'passed' | 'failed';
  schematronStatus: 'not run' | 'passed' | 'failed';
}

/**
 * Status strip: TAC, decode, preview, validation.
 *
 * @param props.hasTac - Editor has non-empty TAC
 * @param props.previewState - Waiting, current, or incomplete
 * @param props.lintStatus - Live TAC lint word
 * @param props.schemaStatus - XML schema word
 * @param props.schematronStatus - Schematron word
 * @example
 * const _ = true;
 */
export function LiveConvertStatusStrip({
  hasTac,
  decodeReady,
  decodeLoading,
  previewState,
  lintStatus,
  schemaStatus,
  schematronStatus,
}: LiveConvertStatusStripProps) {
  const tacLabel = hasTac ? 'TAC entered' : 'TAC empty';
  const decodeLabel = decodeLoading
    ? 'Decode running'
    : decodeReady
      ? 'Decode ready'
      : 'Decode waiting';
  const previewLabel =
    previewState === 'incomplete'
      ? 'Preview incomplete'
      : previewState === 'current'
        ? 'Preview up to date'
        : 'Preview waiting';
  const labels = [
    tacLabel,
    `TAC lint: ${lintStatus}`,
    decodeLabel,
    previewLabel,
    `XML schema: ${schemaStatus}`,
    `Schematron: ${schematronStatus}`,
  ];

  return (
    <ol
      data-testid="convert-status-strip"
      aria-label="Convert progress"
      className="mb-3 flex flex-wrap gap-2 text-xs text-gray-700 dark:text-gray-200"
    >
      {labels.map((label) => (
        <li
          key={label}
          className="rounded-full border border-gray-300 px-2 py-1 dark:border-gray-600"
        >
          {label}
        </li>
      ))}
    </ol>
  );
}
