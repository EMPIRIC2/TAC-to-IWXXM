/**
 * Mapping bridge — TAC group → template match → IWXXM block (Convert + Profile).
 */

import {
  MAPPING_BRIDGE_COL_IWXXM,
  MAPPING_BRIDGE_COL_TAC,
  MAPPING_BRIDGE_COL_TEMPLATE,
  MAPPING_BRIDGE_EMPTY_IWXXM,
  MAPPING_BRIDGE_HEADING,
  MAPPING_BRIDGE_HELP,
  MAPPING_BRIDGE_MATCHED,
  MAPPING_BRIDGE_UNMATCHED,
  MAPPING_BRIDGE_UNMATCHED_HINT,
  PROFILES_CONV_TEMPLATES_SKIP_CHIP,
} from '../../utils/conversionProfilesCopy';

export type MappingBridgeSkipChip = {
  label: string;
  gloss?: string;
};

export type MappingBridgeProps = {
  tacGroup: string;
  templateName?: string;
  matched: boolean | null;
  iwxxmBlock: string;
  skipChips?: MappingBridgeSkipChip[];
  /** When true, show AC11 fail-closed hint for unmatched groups. */
  showUnmatchedHint?: boolean;
};

/**
 * Three-column mapping bridge visualization.
 *
 * @param props.tacGroup - Focused TAC group / token
 * @param props.templateName - Matched conversion rule display name
 * @param props.matched - Preview match result (null = not run)
 * @param props.iwxxmBlock - Preview XML fragment
 * @param props.skipChips - Skipped slot chips from preview
 * @param props.showUnmatchedHint - Show fail-closed copy when unmatched
 */
export function MappingBridge({
  tacGroup,
  templateName,
  matched,
  iwxxmBlock,
  skipChips = [],
  showUnmatchedHint = true,
}: MappingBridgeProps) {
  const matchLabel =
    matched === null
      ? '—'
      : matched
        ? MAPPING_BRIDGE_MATCHED
        : MAPPING_BRIDGE_UNMATCHED;

  return (
    <section
      className="space-y-3 rounded-md border border-gray-200 p-3 dark:border-gray-700"
      data-testid="mapping-bridge"
      aria-label={MAPPING_BRIDGE_HEADING}
    >
      <div>
        <h3 className="text-sm font-medium">{MAPPING_BRIDGE_HEADING}</h3>
        <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
          {MAPPING_BRIDGE_HELP}
        </p>
      </div>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        <div
          className="rounded border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-900"
          data-testid="mapping-bridge-col-tac"
        >
          <h4 className="text-xs font-medium uppercase tracking-wide text-gray-500">
            {MAPPING_BRIDGE_COL_TAC}
          </h4>
          <pre className="mt-2 overflow-auto whitespace-pre-wrap font-mono text-sm text-gray-900 dark:text-gray-100">
            {tacGroup || '—'}
          </pre>
        </div>
        <div
          className="rounded border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-900"
          data-testid="mapping-bridge-col-template"
        >
          <h4 className="text-xs font-medium uppercase tracking-wide text-gray-500">
            {MAPPING_BRIDGE_COL_TEMPLATE}
          </h4>
          <p className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">
            {templateName || '—'}
          </p>
          <p
            className={`mt-1 text-xs ${
              matched === false
                ? 'text-amber-800 dark:text-amber-200'
                : 'text-gray-600 dark:text-gray-400'
            }`}
            data-testid="mapping-bridge-match-status"
          >
            {matchLabel}
          </p>
          {matched === false && showUnmatchedHint ? (
            <p
              className="mt-2 text-xs text-amber-800 dark:text-amber-200"
              data-testid="mapping-bridge-unmatched-hint"
            >
              {MAPPING_BRIDGE_UNMATCHED_HINT}
            </p>
          ) : null}
        </div>
        <div
          className="rounded border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-900"
          data-testid="mapping-bridge-col-iwxxm"
        >
          <h4 className="text-xs font-medium uppercase tracking-wide text-gray-500">
            {MAPPING_BRIDGE_COL_IWXXM}
          </h4>
          <pre
            className="mt-2 max-h-48 overflow-auto whitespace-pre-wrap font-mono text-xs text-gray-900 dark:text-gray-100"
            data-testid="mapping-bridge-iwxxm-block"
          >
            {iwxxmBlock || MAPPING_BRIDGE_EMPTY_IWXXM}
          </pre>
        </div>
      </div>
      {skipChips.length > 0 ? (
        <div className="flex flex-wrap gap-1" data-testid="mapping-bridge-skip-chips">
          {skipChips.map((chip) => (
            <span
              key={chip.label}
              className="rounded bg-amber-100 px-2 py-0.5 text-xs text-amber-900 dark:bg-amber-900/40 dark:text-amber-100"
            >
              {PROFILES_CONV_TEMPLATES_SKIP_CHIP}: {chip.label}
              {chip.gloss ? ` — ${chip.gloss}` : ''}
            </span>
          ))}
        </div>
      ) : null}
    </section>
  );
}
