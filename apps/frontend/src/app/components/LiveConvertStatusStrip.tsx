/**
 * Progress for the live Convert screen. Labels describe state. They do not
 * block editing, preview, or validate, and they do not run schema or Schematron.
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

type StatusTone = 'ready' | 'caution' | 'problem' | 'idle';

interface StatusItem {
  label: string;
  tone: StatusTone;
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
  const items: StatusItem[] = [
    reportItem(hasTac),
    lintItem(lintStatus),
    decodeItem(decodeLoading, decodeReady),
    previewItem(previewState),
    checkItem('XML schema', schemaStatus),
    checkItem('Schematron', schematronStatus),
  ];

  return (
    <div data-testid="convert-status-strip" className="mb-3">
      <p className="mb-2 text-sm text-gray-700 dark:text-gray-200">
        Enter the report in the text area below. Each note says whether that check has
        run.
      </p>
      <ol aria-label="Convert progress" className="flex flex-wrap gap-2 text-xs">
        {items.map((item) => (
          <li
            key={item.label}
            data-tone={item.tone}
            className={`rounded-full border px-2 py-1 ${toneClass(item.tone)}`}
          >
            {item.label}
          </li>
        ))}
      </ol>
    </div>
  );
}

/** Report note: whether the text area has a report. */
function reportItem(hasTac: boolean): StatusItem {
  if (hasTac) {
    return { label: 'Report: entered in the text area below', tone: 'ready' };
  }
  return { label: 'Report: the text area below is empty', tone: 'idle' };
}

/** TAC lint note and its color. */
function lintItem(status: LiveConvertStatusStripProps['lintStatus']): StatusItem {
  if (status === 'passed') {
    return { label: 'TAC lint: passed', tone: 'ready' };
  }
  if (status === 'warnings') {
    return { label: 'TAC lint: warnings', tone: 'caution' };
  }
  if (status === 'failed') {
    return { label: 'TAC lint: failed', tone: 'problem' };
  }
  if (status === 'running') {
    return { label: 'TAC lint: checking the report', tone: 'idle' };
  }
  return { label: 'TAC lint: not run yet', tone: 'idle' };
}

/** Decode note and its color. */
function decodeItem(loading: boolean, ready: boolean): StatusItem {
  if (loading) {
    return { label: 'Decode: running', tone: 'idle' };
  }
  if (ready) {
    return { label: 'Decode: ready', tone: 'ready' };
  }
  return { label: 'Decode: not run yet', tone: 'idle' };
}

/** Preview note and its color. */
function previewItem(state: LiveConvertStatusStripProps['previewState']): StatusItem {
  if (state === 'incomplete') {
    return { label: 'Preview: incomplete', tone: 'caution' };
  }
  if (state === 'current') {
    return { label: 'Preview: up to date', tone: 'ready' };
  }
  return { label: 'Preview: not run yet', tone: 'idle' };
}

/** XML schema or Schematron note and its color. */
function checkItem(
  name: 'XML schema' | 'Schematron',
  status: 'not run' | 'passed' | 'failed',
): StatusItem {
  if (status === 'passed') {
    return { label: `${name}: passed`, tone: 'ready' };
  }
  if (status === 'failed') {
    return { label: `${name}: failed`, tone: 'problem' };
  }
  return {
    label: `${name}: not run yet. It runs when you validate.`,
    tone: 'idle',
  };
}

/** Border and fill classes for one status tone. */
function toneClass(tone: StatusTone): string {
  if (tone === 'ready') {
    return 'border-emerald-400 bg-emerald-50 text-emerald-950 dark:border-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-100';
  }
  if (tone === 'caution') {
    return 'border-amber-400 bg-amber-50 text-amber-950 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-100';
  }
  if (tone === 'problem') {
    return 'border-red-400 bg-red-50 text-red-950 dark:border-red-700 dark:bg-red-950/40 dark:text-red-100';
  }
  return 'border-gray-300 bg-gray-50 text-gray-700 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200';
}
